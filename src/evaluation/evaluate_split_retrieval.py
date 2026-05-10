import argparse
import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config_loader import get_project_root, load_yaml_config
from src.search.semantic_search import semantic_search


@dataclass
class SplitRetrievalCase:
    query: str
    expected_table: str
    expected_source_id: str
    title: str | None = None
    query_type: str = "unknown"
    evaluation_mode: str = "exact_id"


@dataclass
class SplitEvaluationResult:
    split_name: str
    dataset_path: str
    total: int
    total_records: int
    total_eligible: int
    skipped_records: int
    skipped_by_query_type: dict[str, int]
    skipped_by_evaluation_mode: dict[str, int]
    skipped_by_source_table: dict[str, int]
    query_type_counts: dict[str, int]
    evaluation_mode_counts: dict[str, int]
    source_table_counts: dict[str, int]
    filtered_source_table_counts: dict[str, int]
    source_table_metrics: dict[str, dict[str, Any]]
    sample_size: int | None
    top_1_correct: int
    top_k_correct: int
    reciprocal_rank_sum: float
    limit: int
    failures: list[dict[str, Any]]

    @property
    def top_1_accuracy(self) -> float:
        return self.top_1_correct / self.total if self.total else 0.0

    @property
    def top_k_accuracy(self) -> float:
        return self.top_k_correct / self.total if self.total else 0.0

    @property
    def mrr(self) -> float:
        return self.reciprocal_rank_sum / self.total if self.total else 0.0


REQUIRED_TRAINING_KEYS = [
    "validation_dataset_path",
    "test_dataset_path",
]

DEFAULT_EVALUATION_CONFIG = {
    "default_limit": 5,
    "default_query_types": ["specific", "navigational"],
    "default_evaluation_mode": "exact_id",
    "default_source_tables": [],
    "random_sample": False,
    "seed": 42,
    "max_failures": 20,
}


def get_training_config() -> dict[str, Any]:
    """
    config/model.yaml içindeki training ayarlarını döndürür.
    """
    config = load_yaml_config("config/model.yaml")
    training_config = config.get("training")

    if not isinstance(training_config, dict):
        raise KeyError("config/model.yaml içinde training alanı bulunamadı.")

    missing_keys = [
        key for key in REQUIRED_TRAINING_KEYS
        if key not in training_config
    ]

    if missing_keys:
        raise KeyError(
            "Eksik training config alanları: "
            + ", ".join(missing_keys)
        )

    return training_config


def get_split_retrieval_config() -> dict[str, Any]:
    """
    config/model.yaml içindeki split retrieval evaluation ayarlarını döndürür.
    Eksik alanlar için güvenli default değerler kullanılır.
    """
    config = load_yaml_config("config/model.yaml")
    evaluation_config = config.get("evaluation", {})

    if not isinstance(evaluation_config, dict):
        return DEFAULT_EVALUATION_CONFIG.copy()

    split_config = evaluation_config.get("split_retrieval", {})

    if not isinstance(split_config, dict):
        return DEFAULT_EVALUATION_CONFIG.copy()

    merged_config = DEFAULT_EVALUATION_CONFIG.copy()
    merged_config.update(split_config)
    return merged_config


def resolve_project_path(path: str) -> Path:
    return get_project_root() / path


def load_jsonl(path: str) -> list[dict[str, Any]]:
    """
    UTF-8 JSONL dosyasını okur.
    """
    full_path = resolve_project_path(path)

    if not full_path.exists():
        raise FileNotFoundError(
            f"Split dataset bulunamadı: {full_path}\n"
            "Önce şu komutu çalıştırın:\n"
            "python -m src.training.split_training_dataset"
        )

    records: list[dict[str, Any]] = []

    with full_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Geçersiz JSONL satırı: {full_path}:{line_number}"
                ) from exc

            if not isinstance(record, dict):
                raise ValueError(
                    f"JSONL kaydı object olmalı: {full_path}:{line_number}"
                )

            records.append(record)

    return records


def get_expected_source(record: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    expected = record.get("expected")

    if isinstance(expected, dict):
        expected_table = expected.get("source_table") or record.get("source_table")
        expected_source_id = expected.get("source_id") or record.get("source_id")
        expected_title = expected.get("title") or record.get("title")
        return (
            str(expected_table) if expected_table else None,
            str(expected_source_id) if expected_source_id else None,
            str(expected_title) if expected_title else None,
        )

    return (
        str(record["source_table"]) if record.get("source_table") else None,
        str(record["source_id"]) if record.get("source_id") else None,
        str(record["title"]) if record.get("title") else None,
    )


def build_cases(records: list[dict[str, Any]], dataset_path: str) -> list[SplitRetrievalCase]:
    """
    JSONL kayıtlarını evaluation case formatına dönüştürür.
    """
    cases: list[SplitRetrievalCase] = []

    for index, record in enumerate(records, start=1):
        query = record.get("query")
        source_table, source_id, title = get_expected_source(record)
        query_type = record.get("query_type", "unknown")
        evaluation_mode = record.get("evaluation_mode", "exact_id")

        if "query_type" not in record or "evaluation_mode" not in record:
            print(
                "Uyarı: query_type/evaluation_mode eksik; geriye dönük defaultlar kullanıldı. "
                f"Dosya: {dataset_path}, kayıt: {index}"
            )

        if not query:
            print(
                "Uyarı: query boş olduğu için evaluation kaydı atlandı. "
                f"Dosya: {dataset_path}, kayıt: {index}"
            )
            continue

        if not source_table or not source_id:
            raise ValueError(
                f"{dataset_path} içindeki {index}. kayıtta source_table/source_id eksik."
            )

        cases.append(
            SplitRetrievalCase(
                query=str(query),
                expected_table=str(source_table),
                expected_source_id=str(source_id),
                title=title,
                query_type=str(query_type),
                evaluation_mode=str(evaluation_mode),
            )
        )

    return cases


def case_is_evaluable(
    test_case: SplitRetrievalCase,
    query_types: set[str] | None,
    evaluation_mode: str,
    include_generic: bool,
) -> bool:
    if include_generic and test_case.query_type == "generic":
        return True

    if query_types is not None and test_case.query_type not in query_types:
        return False

    return test_case.evaluation_mode == evaluation_mode


def filter_cases(
    cases: list[SplitRetrievalCase],
    query_types: list[str] | None,
    evaluation_mode: str,
    include_generic: bool,
    source_tables: list[str] | None,
) -> tuple[list[SplitRetrievalCase], dict[str, Any]]:
    query_type_filter = set(query_types) if query_types else None
    source_table_filter = set(source_tables) if source_tables else None
    mode_type_filtered_cases: list[SplitRetrievalCase] = []
    filtered_cases: list[SplitRetrievalCase] = []
    skipped_by_query_type: Counter[str] = Counter()
    skipped_by_evaluation_mode: Counter[str] = Counter()
    skipped_by_source_table: Counter[str] = Counter()

    for test_case in cases:
        if query_type_filter is not None and test_case.query_type not in query_type_filter:
            skipped_by_query_type[test_case.query_type] += 1
            continue

        if not (include_generic and test_case.query_type == "generic"):
            if test_case.evaluation_mode != evaluation_mode:
                skipped_by_evaluation_mode[test_case.evaluation_mode] += 1
                continue

        if not case_is_evaluable(test_case, query_type_filter, evaluation_mode, include_generic):
            # Güvenli fallback; normalde yukarıdaki dallar bu durumu kapsar.
            skipped_by_evaluation_mode[test_case.evaluation_mode] += 1
            continue

        mode_type_filtered_cases.append(test_case)

        if source_table_filter is not None and test_case.expected_table not in source_table_filter:
            skipped_by_source_table[test_case.expected_table] += 1
            continue

        filtered_cases.append(test_case)

    stats = {
        "query_type_counts": dict(Counter(case.query_type for case in cases)),
        "evaluation_mode_counts": dict(Counter(case.evaluation_mode for case in cases)),
        "source_table_counts": dict(Counter(case.expected_table for case in cases)),
        "filtered_source_table_counts": dict(Counter(case.expected_table for case in filtered_cases)),
        "skipped_by_query_type": dict(skipped_by_query_type),
        "skipped_by_evaluation_mode": dict(skipped_by_evaluation_mode),
        "skipped_by_source_table": dict(skipped_by_source_table),
        "mode_type_filtered_count": len(mode_type_filtered_cases),
    }

    return filtered_cases, stats


def apply_sample(
    cases: list[SplitRetrievalCase],
    sample_size: int | None,
    random_sample: bool,
    seed: int,
) -> list[SplitRetrievalCase]:
    if sample_size is None:
        return cases

    if sample_size <= 0:
        raise ValueError("sample_size pozitif bir integer olmalı.")

    if sample_size >= len(cases):
        return cases

    if random_sample:
        return random.Random(seed).sample(cases, sample_size)

    return cases[:sample_size]


def result_matches_expected(
    result: dict[str, Any],
    expected_table: str,
    expected_source_id: str,
) -> bool:
    """
    Semantic search sonucunun beklenen source_table/source_id kaydı olup olmadığını kontrol eder.
    """
    return (
        str(result.get("kaynak_tablo")) == expected_table
        and str(result.get("kaynak_id")) == expected_source_id
    )


def evaluate_case(test_case: SplitRetrievalCase, limit: int) -> dict[str, Any]:
    """
    Tek query için Top-1 ve Top-K eşleşmesini hesaplar.
    """
    results = semantic_search(test_case.query, limit=limit)

    top_1_match = False
    top_k_match = False
    expected_rank: int | None = None

    if results:
        top_1_match = result_matches_expected(
            results[0],
            test_case.expected_table,
            test_case.expected_source_id,
        )
        for index, result in enumerate(results, start=1):
            if result_matches_expected(
                result,
                test_case.expected_table,
                test_case.expected_source_id,
            ):
                expected_rank = index
                break

        top_k_match = expected_rank is not None

    return {
        "query": test_case.query,
        "expected_table": test_case.expected_table,
        "expected_source_id": test_case.expected_source_id,
        "expected_title": test_case.title,
        "top_1_match": top_1_match,
        "top_k_match": top_k_match,
        "expected_rank": expected_rank,
        "reciprocal_rank": 1 / expected_rank if expected_rank is not None else 0.0,
        "result_count": len(results),
        "top_1_table": results[0]["kaynak_tablo"] if results else None,
        "top_1_source_id": str(results[0]["kaynak_id"]) if results else None,
        "top_1_title": results[0]["baslik"] if results else None,
        "top_1_score": results[0]["similarity_score"] if results else None,
    }


def evaluate_split(
    split_name: str,
    dataset_path: str,
    limit: int = 5,
    max_failures: int = 10,
    sample_size: int | None = None,
    query_types: list[str] | None = None,
    evaluation_mode: str = "exact_id",
    include_generic: bool = False,
    source_tables: list[str] | None = None,
    random_sample: bool = False,
    seed: int = 42,
) -> SplitEvaluationResult:
    """
    Belirli bir split dosyası için retrieval evaluation çalıştırır.
    """
    records = load_jsonl(dataset_path)
    all_cases = build_cases(records, dataset_path)
    eligible_cases, filter_stats = filter_cases(
        cases=all_cases,
        query_types=query_types,
        evaluation_mode=evaluation_mode,
        include_generic=include_generic,
        source_tables=source_tables,
    )
    cases = apply_sample(eligible_cases, sample_size, random_sample, seed)

    print("\n" + "=" * 80)
    print(f"{split_name.upper()} RETRIEVAL EVALUATION")
    print("=" * 80)
    print(f"Dataset           : {dataset_path}")
    print(f"Total records     : {len(all_cases)}")
    print(f"Mode/type filtered: {filter_stats['mode_type_filtered_count']}")
    print(f"Evaluated records : {len(cases)}")
    print(f"Skipped records   : {len(all_cases) - len(eligible_cases)}")
    print(f"Query types       : {format_counts(filter_stats['query_type_counts'])}")
    print(f"Evaluation modes  : {format_counts(filter_stats['evaluation_mode_counts'])}")
    print(f"Source tables     : {format_counts(filter_stats['filtered_source_table_counts'])}")
    if filter_stats["skipped_by_query_type"]:
        print(f"Skipped by type   : {format_counts(filter_stats['skipped_by_query_type'])}")
    if filter_stats["skipped_by_evaluation_mode"]:
        print(f"Skipped by mode   : {format_counts(filter_stats['skipped_by_evaluation_mode'])}")
    if filter_stats["skipped_by_source_table"]:
        print(f"Skipped by table  : {format_counts(filter_stats['skipped_by_source_table'])}")
    if sample_size is not None:
        sample_mode = "random" if random_sample else "first"
        print(f"Sample           : {len(cases)} / {len(eligible_cases)} ({sample_mode})")
    print(f"Top-K             : {limit}")
    print(f"Evaluation mode   : {evaluation_mode}")
    print(f"Query type filter : {', '.join(query_types or []) if query_types else 'Yok'}")
    print(f"Source table filter: {', '.join(source_tables or []) if source_tables else 'Yok'}")

    top_1_correct = 0
    top_k_correct = 0
    reciprocal_rank_sum = 0.0
    failures: list[dict[str, Any]] = []
    source_table_metrics: dict[str, dict[str, Any]] = {}

    for index, test_case in enumerate(cases, start=1):
        case_result = evaluate_case(test_case, limit=limit)
        table_metrics = source_table_metrics.setdefault(
            test_case.expected_table,
            {
                "total": 0,
                "top_1_correct": 0,
                "top_k_correct": 0,
                "reciprocal_rank_sum": 0.0,
            },
        )
        table_metrics["total"] += 1

        if case_result["top_1_match"]:
            top_1_correct += 1
            table_metrics["top_1_correct"] += 1

        if case_result["top_k_match"]:
            top_k_correct += 1
            reciprocal_rank_sum += float(case_result["reciprocal_rank"])
            table_metrics["top_k_correct"] += 1
            table_metrics["reciprocal_rank_sum"] += float(case_result["reciprocal_rank"])
        elif len(failures) < max_failures:
            failures.append(case_result)

        if index % 25 == 0 or index == len(cases):
            print(f"İşlenen kayıt: {index}/{len(cases)}")

    result = SplitEvaluationResult(
        split_name=split_name,
        dataset_path=dataset_path,
        total=len(cases),
        total_records=len(all_cases),
        total_eligible=len(eligible_cases),
        skipped_records=len(all_cases) - len(eligible_cases),
        skipped_by_query_type=filter_stats["skipped_by_query_type"],
        skipped_by_evaluation_mode=filter_stats["skipped_by_evaluation_mode"],
        skipped_by_source_table=filter_stats["skipped_by_source_table"],
        query_type_counts=filter_stats["query_type_counts"],
        evaluation_mode_counts=filter_stats["evaluation_mode_counts"],
        source_table_counts=filter_stats["source_table_counts"],
        filtered_source_table_counts=filter_stats["filtered_source_table_counts"],
        source_table_metrics=source_table_metrics,
        sample_size=sample_size,
        top_1_correct=top_1_correct,
        top_k_correct=top_k_correct,
        reciprocal_rank_sum=reciprocal_rank_sum,
        limit=limit,
        failures=failures,
    )

    print_split_summary(result)
    return result


def print_split_summary(result: SplitEvaluationResult) -> None:
    print("\nSonuç:")
    if result.sample_size is not None:
        print(f"Örneklem         : {result.total}/{result.total_eligible}")
    print(f"Top-1 doğru      : {result.top_1_correct}/{result.total}")
    print(f"Top-{result.limit} doğru      : {result.top_k_correct}/{result.total}")
    print(f"Top-1 Accuracy   : {result.top_1_accuracy:.4f}")
    print(f"Top-{result.limit} Accuracy   : {result.top_k_accuracy:.4f}")
    print(f"MRR              : {result.mrr:.4f}")
    print_source_table_summary(result.source_table_metrics, result.limit)

    if not result.failures:
        return

    print("\nİlk başarısız Top-K örnekleri:")
    for failure in result.failures:
        print("-" * 80)
        print(f"Sorgu          : {failure['query']}")
        print(f"Beklenen       : {failure['expected_table']} / {failure['expected_source_id']}")
        print(f"Beklenen başlık: {failure['expected_title']}")
        print(f"Top-1          : {failure['top_1_table']} / {failure['top_1_source_id']}")
        print(f"Top-1 başlık   : {failure['top_1_title']}")
        score = failure["top_1_score"]
        print(f"Top-1 skor     : {score:.4f}" if score is not None else "Top-1 skor     : Yok")


def evaluate_configured_splits(
    split: str = "all",
    limit: int = 5,
    max_failures: int = 10,
    sample_size: int | None = None,
    query_types: list[str] | None = None,
    evaluation_mode: str = "exact_id",
    include_generic: bool = False,
    source_tables: list[str] | None = None,
    random_sample: bool = False,
    seed: int = 42,
) -> list[SplitEvaluationResult]:
    """
    Config'teki validation/test splitleri için evaluation çalıştırır.
    """
    training_config = get_training_config()
    split_paths = {
        "validation": training_config["validation_dataset_path"],
        "test": training_config["test_dataset_path"],
    }

    if split not in {"validation", "test", "all"}:
        raise ValueError("split değeri validation, test veya all olmalı.")

    selected_splits = (
        split_paths.items()
        if split == "all"
        else [(split, split_paths[split])]
    )

    results = [
        evaluate_split(
            split_name=split_name,
            dataset_path=dataset_path,
            limit=limit,
            max_failures=max_failures,
            sample_size=sample_size,
            query_types=query_types,
            evaluation_mode=evaluation_mode,
            include_generic=include_generic,
            source_tables=source_tables,
            random_sample=random_sample,
            seed=seed,
        )
        for split_name, dataset_path in selected_splits
    ]

    if len(results) > 1:
        print_overall_summary(results)

    return results


def print_overall_summary(results: list[SplitEvaluationResult]) -> None:
    total = sum(result.total for result in results)
    top_1_correct = sum(result.top_1_correct for result in results)
    top_k_correct = sum(result.top_k_correct for result in results)
    reciprocal_rank_sum = sum(result.reciprocal_rank_sum for result in results)
    limit = results[0].limit if results else 5

    top_1_accuracy = top_1_correct / total if total else 0.0
    top_k_accuracy = top_k_correct / total if total else 0.0
    mrr = reciprocal_rank_sum / total if total else 0.0

    print("\n" + "#" * 80)
    print("GENEL SPLIT RETRIEVAL DEĞERLENDİRMESİ")
    print("#" * 80)
    print(f"Toplam case       : {total}")
    if any(result.sample_size is not None for result in results):
        total_available = sum(result.total_eligible for result in results)
        print(f"Örneklem          : {total}/{total_available}")
    print(f"Top-1 doğru       : {top_1_correct}/{total}")
    print(f"Top-{limit} doğru       : {top_k_correct}/{total}")
    print(f"Top-1 Accuracy    : {top_1_accuracy:.4f}")
    print(f"Top-{limit} Accuracy    : {top_k_accuracy:.4f}")
    print(f"MRR               : {mrr:.4f}")
    combined_metrics: dict[str, dict[str, Any]] = {}
    for result in results:
        for table, metrics in result.source_table_metrics.items():
            target = combined_metrics.setdefault(
                table,
                {
                    "total": 0,
                    "top_1_correct": 0,
                    "top_k_correct": 0,
                    "reciprocal_rank_sum": 0.0,
                },
            )
            target["total"] += metrics["total"]
            target["top_1_correct"] += metrics["top_1_correct"]
            target["top_k_correct"] += metrics["top_k_correct"]
            target["reciprocal_rank_sum"] += metrics["reciprocal_rank_sum"]

    print_source_table_summary(combined_metrics, limit)


def format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "Yok"

    return ", ".join(
        f"{key}={value}"
        for key, value in sorted(counts.items())
    )


def print_source_table_summary(
    source_table_metrics: dict[str, dict[str, Any]],
    limit: int,
) -> None:
    if not source_table_metrics:
        return

    print("\nSource table bazlı sonuç:")
    for table, metrics in sorted(source_table_metrics.items()):
        total = metrics["total"]
        top_1_correct = metrics["top_1_correct"]
        top_k_correct = metrics["top_k_correct"]
        reciprocal_rank_sum = metrics["reciprocal_rank_sum"]

        top_1_accuracy = top_1_correct / total if total else 0.0
        top_k_accuracy = top_k_correct / total if total else 0.0
        mrr = reciprocal_rank_sum / total if total else 0.0

        print(
            f"{table:<16} | "
            f"total={total:<4} | "
            f"top1={top_1_correct:<4} | "
            f"top{limit}={top_k_correct:<4} | "
            f"top1_acc={top_1_accuracy:.4f} | "
            f"top{limit}_acc={top_k_accuracy:.4f} | "
            f"mrr={mrr:.4f}"
        )


def parse_args() -> argparse.Namespace:
    evaluation_config = get_split_retrieval_config()
    parser = argparse.ArgumentParser(
        description="Validation/test JSONL splitleri üzerinden retrieval evaluation çalıştırır."
    )
    parser.add_argument(
        "--split",
        choices=["validation", "test", "all"],
        default="all",
        help="Çalıştırılacak split.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=int(evaluation_config.get("default_limit", 5)),
        help="Top-K değerlendirme limiti.",
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=int(evaluation_config.get("max_failures", 20)),
        help="Her split için ekrana basılacak maksimum başarısız örnek sayısı.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Her split için değerlendirilecek ilk N kayıt. Verilmezse tüm split çalışır.",
    )
    parser.add_argument(
        "--query-type",
        nargs="+",
        default=None,
        help="Değerlendirilecek query_type değerleri. Örn: --query-type specific navigational",
    )
    parser.add_argument(
        "--evaluation-mode",
        default=evaluation_config.get("default_evaluation_mode", "exact_id"),
        help="Değerlendirilecek evaluation_mode. Varsayılan: exact_id",
    )
    parser.add_argument(
        "--include-generic",
        action="store_true",
        help="Generic kayıtları da exact-id metriğine dahil eder.",
    )
    parser.add_argument(
        "--source-table",
        nargs="+",
        default=None,
        help="Değerlendirilecek source_table değerleri.",
    )
    parser.add_argument(
        "--random-sample",
        action="store_true",
        default=bool(evaluation_config.get("random_sample", False)),
        help="sample-size verildiyse ilk N yerine random N kayıt seçer.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=int(evaluation_config.get("seed", 42)),
        help="Random sample seed değeri.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config_query_types = get_split_retrieval_config().get("default_query_types", [])
    config_source_tables = get_split_retrieval_config().get("default_source_tables", [])
    query_types = args.query_type or list(config_query_types)
    source_tables = args.source_table or list(config_source_tables)
    evaluate_configured_splits(
        split=args.split,
        limit=args.limit,
        max_failures=args.max_failures,
        sample_size=args.sample_size,
        query_types=query_types,
        evaluation_mode=args.evaluation_mode,
        include_generic=args.include_generic,
        source_tables=source_tables,
        random_sample=args.random_sample,
        seed=args.seed,
    )
