import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

from src.config_loader import get_project_root, load_yaml_config


def get_model_config() -> dict[str, Any]:
    config = load_yaml_config("config/model.yaml")
    return config["model"]


def get_training_config() -> dict[str, Any]:
    config = load_yaml_config("config/model.yaml")
    return config["training"]


def get_loss_config() -> dict[str, Any]:
    config = load_yaml_config("config/model.yaml")
    return config.get("loss", {"name": "MultipleNegativesRankingLoss"})


def set_seed(seed: int) -> None:
    """
    Eğitim sonuçlarının daha tekrar üretilebilir olması için seed ayarlar.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_training_pairs(dataset_path: str) -> list[dict[str, Any]]:
    """
    JSONL formatındaki query-positive_text eğitim çiftlerini okur.
    """
    full_path = get_project_root() / dataset_path

    if not full_path.exists():
        raise FileNotFoundError(f"Training dataset bulunamadı: {full_path}")

    pairs: list[dict[str, Any]] = []

    with full_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            query = record.get("query")
            positive_text = record.get("positive_text")

            if not query or not positive_text:
                continue

            pairs.append(record)

    return pairs


def build_input_examples(pairs: list[dict[str, Any]]) -> list[InputExample]:
    """
    SentenceTransformer eğitim formatına çevirir.

    Her örnek:
        texts[0] = kullanıcı sorgusu
        texts[1] = doğru eşleşmesi gereken veritabanı metni
    """
    examples: list[InputExample] = []

    for pair in pairs:
        examples.append(
            InputExample(
                texts=[
                    pair["query"],
                    pair["positive_text"],
                ]
            )
        )

    return examples


def create_train_loss(model: SentenceTransformer):
    """
    Config'e göre loss fonksiyonunu oluşturur.
    """
    loss_config = get_loss_config()
    loss_name = loss_config.get("name", "MultipleNegativesRankingLoss")

    if loss_name != "MultipleNegativesRankingLoss":
        raise ValueError(f"Desteklenmeyen loss fonksiyonu: {loss_name}")

    return losses.MultipleNegativesRankingLoss(model)


def train() -> None:
    model_config = get_model_config()
    training_config = get_training_config()

    seed = int(training_config.get("random_seed", 42))
    set_seed(seed)

    dataset_path = training_config["train_dataset_path"]
    output_dir = training_config["output_dir"]

    batch_size = int(training_config.get("batch_size", 16))
    epochs = int(training_config.get("epochs", 1))
    warmup_ratio = float(training_config.get("warmup_ratio", 0.1))
    learning_rate = float(training_config.get("learning_rate", 2e-5))

    base_model_name = model_config["base_model_name"]

    print("=" * 80)
    print("FINE-TUNING BAŞLIYOR")
    print("=" * 80)
    print(f"Base model       : {base_model_name}")
    print(f"Dataset          : {dataset_path}")
    print(f"Output directory : {output_dir}")
    print(f"Epochs           : {epochs}")
    print(f"Batch size       : {batch_size}")
    print(f"Learning rate    : {learning_rate}")

    pairs = load_training_pairs(dataset_path)
    print(f"Training pair sayısı: {len(pairs)}")

    if not pairs:
        raise ValueError("Eğitim için uygun training pair bulunamadı.")

    train_examples = build_input_examples(pairs)
    train_dataloader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=batch_size,
    )

    warmup_steps = int(len(train_dataloader) * epochs * warmup_ratio)

    print(f"Batch sayısı      : {len(train_dataloader)}")
    print(f"Warmup steps      : {warmup_steps}")

    model = SentenceTransformer(base_model_name)
    train_loss = create_train_loss(model)

    full_output_path = get_project_root() / output_dir
    full_output_path.mkdir(parents=True, exist_ok=True)

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=warmup_steps,
        optimizer_params={"lr": learning_rate},
        output_path=str(full_output_path),
        show_progress_bar=True,
    )

    print("=" * 80)
    print("FINE-TUNING TAMAMLANDI")
    print("=" * 80)
    print(f"Model kaydedildi: {full_output_path}")


if __name__ == "__main__":
    train()