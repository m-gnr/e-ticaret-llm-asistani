import argparse
import json
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


@dataclass
class SplitEvaluationResult:
    split_name: str
    dataset_path: str
    total: int
    total_available: int
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


def build_cases(records: list[dict[str, Any]], dataset_path: str) -> list[SplitRetrievalCase]:
    """
    JSONL kayıtlarını evaluation case formatına dönüştürür.
    """
    cases: list[SplitRetrievalCase] = []

    for index, record in enumerate(records, start=1):
        query = record.get("query")
        source_table = record.get("source_table")
        source_id = record.get("source_id")

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
                title=record.get("title"),
            )
        )

    return cases


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
) -> SplitEvaluationResult:
    """
    Belirli bir split dosyası için retrieval evaluation çalıştırır.
    """
    records = load_jsonl(dataset_path)
    all_cases = build_cases(records, dataset_path)

    if sample_size is not None:
        if sample_size <= 0:
            raise ValueError("sample_size pozitif bir integer olmalı.")
        cases = all_cases[:sample_size]
    else:
        cases = all_cases

    print("\n" + "=" * 80)
    print(f"{split_name.upper()} RETRIEVAL EVALUATION")
    print("=" * 80)
    print(f"Dataset : {dataset_path}")
    if sample_size is not None:
        print(f"Case    : {len(cases)} / {len(all_cases)} sampled")
    else:
        print(f"Case    : {len(cases)}")
    print(f"Top-K   : {limit}")

    top_1_correct = 0
    top_k_correct = 0
    reciprocal_rank_sum = 0.0
    failures: list[dict[str, Any]] = []

    for index, test_case in enumerate(cases, start=1):
        case_result = evaluate_case(test_case, limit=limit)

        if case_result["top_1_match"]:
            top_1_correct += 1

        if case_result["top_k_match"]:
            top_k_correct += 1
            reciprocal_rank_sum += float(case_result["reciprocal_rank"])
        elif len(failures) < max_failures:
            failures.append(case_result)

        if index % 25 == 0 or index == len(cases):
            print(f"İşlenen kayıt: {index}/{len(cases)}")

    result = SplitEvaluationResult(
        split_name=split_name,
        dataset_path=dataset_path,
        total=len(cases),
        total_available=len(all_cases),
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
        print(f"Örneklem         : {result.total}/{result.total_available}")
    print(f"Top-1 doğru      : {result.top_1_correct}/{result.total}")
    print(f"Top-{result.limit} doğru      : {result.top_k_correct}/{result.total}")
    print(f"Top-1 Accuracy   : {result.top_1_accuracy:.4f}")
    print(f"Top-{result.limit} Accuracy   : {result.top_k_accuracy:.4f}")
    print(f"MRR              : {result.mrr:.4f}")

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
        total_available = sum(result.total_available for result in results)
        print(f"Örneklem          : {total}/{total_available}")
    print(f"Top-1 doğru       : {top_1_correct}/{total}")
    print(f"Top-{limit} doğru       : {top_k_correct}/{total}")
    print(f"Top-1 Accuracy    : {top_1_accuracy:.4f}")
    print(f"Top-{limit} Accuracy    : {top_k_accuracy:.4f}")
    print(f"MRR               : {mrr:.4f}")


def parse_args() -> argparse.Namespace:
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
        default=5,
        help="Top-K değerlendirme limiti.",
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=10,
        help="Her split için ekrana basılacak maksimum başarısız örnek sayısı.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Her split için değerlendirilecek ilk N kayıt. Verilmezse tüm split çalışır.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    evaluate_configured_splits(
        split=args.split,
        limit=args.limit,
        max_failures=args.max_failures,
        sample_size=args.sample_size,
    )
