import json
import random
from pathlib import Path
from typing import Any

from src.config_loader import get_project_root, load_yaml_config


REQUIRED_TRAINING_KEYS = [
    "full_dataset_path",
    "train_dataset_path",
    "validation_dataset_path",
    "test_dataset_path",
]

REQUIRED_SPLIT_KEYS = [
    "train_ratio",
    "validation_ratio",
    "test_ratio",
    "group_by",
    "shuffle",
]

REQUIRED_RECORD_KEYS = [
    "query",
    "positive_text",
    "source_table",
    "source_id",
]


def get_training_config() -> dict[str, Any]:
    """
    model.yaml içindeki training ayarlarını döndürür.
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


def get_split_config() -> dict[str, Any]:
    """
    model.yaml içindeki dataset_split ayarlarını döndürür.
    """
    config = load_yaml_config("config/model.yaml")
    split_config = config.get("dataset_split")

    if not isinstance(split_config, dict):
        raise KeyError("config/model.yaml içinde dataset_split alanı bulunamadı.")

    missing_keys = [
        key for key in REQUIRED_SPLIT_KEYS
        if key not in split_config
    ]

    if missing_keys:
        raise KeyError(
            "Eksik dataset_split config alanları: "
            + ", ".join(missing_keys)
        )

    validate_split_ratios(split_config)
    return split_config


def validate_split_ratios(split_config: dict[str, Any]) -> None:
    train_ratio = float(split_config["train_ratio"])
    validation_ratio = float(split_config["validation_ratio"])
    test_ratio = float(split_config["test_ratio"])
    total = train_ratio + validation_ratio + test_ratio

    if abs(total - 1.0) > 1e-6:
        raise ValueError(
            "Dataset split oranları toplamı 1.0 olmalı. "
            f"Gelen toplam: {total:.6f}"
        )


def resolve_project_path(path: str) -> Path:
    return get_project_root() / path


def load_jsonl(path: str) -> list[dict[str, Any]]:
    """
    UTF-8 JSONL dosyasını okur.
    """
    full_path = resolve_project_path(path)

    if not full_path.exists():
        raise FileNotFoundError(f"Dataset dosyası bulunamadı: {full_path}")

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


def save_jsonl(records: list[dict[str, Any]], path: str) -> Path:
    """
    Kayıtları UTF-8 JSONL formatında kaydeder.
    """
    full_path = resolve_project_path(path)
    full_path.parent.mkdir(parents=True, exist_ok=True)

    with full_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    return full_path


def validate_record(record: dict[str, Any], index: int) -> bool:
    """
    Split için gerekli alanları kontrol eder.

    Boş query/positive_text kayıtları atlanır. source_table/source_id eksikse
    group-based split güvenilir olmayacağı için hata verilir.
    """
    for key in ("source_table", "source_id"):
        if not record.get(key):
            raise ValueError(
                f"{index}. kayıtta zorunlu group alanı eksik veya boş: {key}"
            )

    if not record.get("query") or not record.get("positive_text"):
        print(
            "Uyarı: query veya positive_text boş olduğu için kayıt atlandı. "
            f"Kayıt index: {index}"
        )
        return False

    return True


def filter_valid_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid_records: list[dict[str, Any]] = []

    for index, record in enumerate(records, start=1):
        missing_keys = [key for key in REQUIRED_RECORD_KEYS if key not in record]
        if missing_keys:
            if "source_table" in missing_keys or "source_id" in missing_keys:
                raise ValueError(
                    f"{index}. kayıtta zorunlu alanlar eksik: "
                    + ", ".join(missing_keys)
                )

            print(
                "Uyarı: query veya positive_text alanı eksik olduğu için kayıt atlandı. "
                f"Kayıt index: {index}"
            )
            continue

        if validate_record(record, index):
            valid_records.append(record)

    return valid_records


def get_group_key(record: dict[str, Any], group_by: list[str]) -> tuple[Any, ...]:
    """
    Config'teki group_by alanlarına göre group key üretir.
    """
    missing_keys = [key for key in group_by if not record.get(key)]

    if missing_keys:
        raise ValueError(
            "Group key oluşturmak için zorunlu alanlar eksik veya boş: "
            + ", ".join(missing_keys)
        )

    return tuple(record[key] for key in group_by)


def group_records(
    records: list[dict[str, Any]],
    group_by: list[str],
) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    """
    Kayıtları source_table/source_id gibi group key alanlarına göre grupla.
    """
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}

    for record in records:
        group_key = get_group_key(record, group_by)
        groups.setdefault(group_key, []).append(record)

    return groups


def split_groups(
    groups: dict[tuple[Any, ...], list[dict[str, Any]]],
    split_config: dict[str, Any],
    seed: int,
) -> tuple[
    dict[tuple[Any, ...], list[dict[str, Any]]],
    dict[tuple[Any, ...], list[dict[str, Any]]],
    dict[tuple[Any, ...], list[dict[str, Any]]],
]:
    """
    Group listelerini train/validation/test olarak böler.
    """
    group_items = list(groups.items())

    if split_config.get("shuffle", True):
        random.Random(seed).shuffle(group_items)

    group_count = len(group_items)
    train_end = int(group_count * float(split_config["train_ratio"]))
    validation_end = train_end + int(group_count * float(split_config["validation_ratio"]))

    train_items = group_items[:train_end]
    validation_items = group_items[train_end:validation_end]
    test_items = group_items[validation_end:]

    return dict(train_items), dict(validation_items), dict(test_items)


def flatten_groups(
    groups: dict[tuple[Any, ...], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for group_records_list in groups.values():
        records.extend(group_records_list)

    return records


def validate_no_group_leakage(
    train_groups: dict[tuple[Any, ...], list[dict[str, Any]]],
    validation_groups: dict[tuple[Any, ...], list[dict[str, Any]]],
    test_groups: dict[tuple[Any, ...], list[dict[str, Any]]],
) -> None:
    """
    Aynı group key'in birden fazla split içinde yer almadığını doğrular.
    """
    train_keys = set(train_groups)
    validation_keys = set(validation_groups)
    test_keys = set(test_groups)

    leakage_keys = (
        (train_keys & validation_keys)
        | (train_keys & test_keys)
        | (validation_keys & test_keys)
    )

    if leakage_keys:
        sample = sorted(str(key) for key in leakage_keys)[:5]
        raise ValueError(
            "Group leakage tespit edildi: aynı source_table/source_id "
            "birden fazla split içinde yer alıyor. Örnekler: "
            + ", ".join(sample)
        )


def get_random_seed(
    training_config: dict[str, Any],
    split_config: dict[str, Any],
) -> int:
    if split_config.get("random_seed") is not None:
        return int(split_config["random_seed"])

    if training_config.get("random_seed") is not None:
        return int(training_config["random_seed"])

    return 42


def print_split_examples(split_name: str, records: list[dict[str, Any]]) -> None:
    print(f"\n{split_name} ilk örnekler:")

    if not records:
        print("  Örnek yok.")
        return

    for record in records[:2]:
        print(
            "  - "
            f"{record.get('source_table')} / {record.get('source_id')} | "
            f"{record.get('query')}"
        )


def split_training_dataset() -> None:
    """
    Full query-positive_text datasetini group-based train/val/test splitlerine ayırır.
    """
    training_config = get_training_config()
    split_config = get_split_config()

    full_dataset_path = training_config["full_dataset_path"]
    train_dataset_path = training_config["train_dataset_path"]
    validation_dataset_path = training_config["validation_dataset_path"]
    test_dataset_path = training_config["test_dataset_path"]
    group_by = list(split_config["group_by"])
    seed = get_random_seed(training_config, split_config)

    print("=" * 80)
    print("TRAINING DATASET SPLIT BAŞLIYOR")
    print("=" * 80)
    print(f"Full dataset: {full_dataset_path}")
    print(f"Train output : {train_dataset_path}")
    print(f"Val output   : {validation_dataset_path}")
    print(f"Test output  : {test_dataset_path}")

    records = load_jsonl(full_dataset_path)
    valid_records = filter_valid_records(records)
    groups = group_records(valid_records, group_by)

    print()
    print(f"Toplam kayıt sayısı : {len(valid_records)}")
    print(f"Toplam group sayısı : {len(groups)}")
    print()
    print("Split oranları:")
    print(f"Train: {float(split_config['train_ratio']):.2f}")
    print(f"Val  : {float(split_config['validation_ratio']):.2f}")
    print(f"Test : {float(split_config['test_ratio']):.2f}")

    train_groups, validation_groups, test_groups = split_groups(groups, split_config, seed)
    validate_no_group_leakage(train_groups, validation_groups, test_groups)

    train_records = flatten_groups(train_groups)
    validation_records = flatten_groups(validation_groups)
    test_records = flatten_groups(test_groups)

    train_output = save_jsonl(train_records, train_dataset_path)
    validation_output = save_jsonl(validation_records, validation_dataset_path)
    test_output = save_jsonl(test_records, test_dataset_path)

    print()
    print("Çıktılar:")
    print(f"Train kayıt/group : {len(train_records)} / {len(train_groups)}")
    print(f"Val kayıt/group   : {len(validation_records)} / {len(validation_groups)}")
    print(f"Test kayıt/group  : {len(test_records)} / {len(test_groups)}")
    print()
    print(f"Train dosyası: {train_output}")
    print(f"Val dosyası  : {validation_output}")
    print(f"Test dosyası : {test_output}")

    print_split_examples("Train", train_records)
    print_split_examples("Val", validation_records)
    print_split_examples("Test", test_records)

    print()
    print("Dataset split tamamlandı.")
    print("=" * 80)


if __name__ == "__main__":
    split_training_dataset()
