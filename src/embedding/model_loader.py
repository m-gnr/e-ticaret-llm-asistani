from pathlib import Path
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config_loader import get_project_root, load_yaml_config


_EMBEDDING_MODEL_CACHE: SentenceTransformer | None = None


def get_model_config() -> dict:
    """
    config/model.yaml dosyasındaki model ayarlarını okur.
    """
    config = load_yaml_config("config/model.yaml")
    return config["model"]


def get_tokenizer_config() -> dict:
    """
    config/model.yaml dosyasındaki tokenizer ayarlarını okur.
    """
    config = load_yaml_config("config/model.yaml")
    return config.get("tokenizer", {})


def resolve_model_path() -> str:
    """
    Fine-tuned model klasörü varsa onu döndürür.
    Yoksa base model adını döndürür.

    Böylece sistem önce kendi eğitilmiş modelimizi kullanır.
    Eğer model henüz eğitilmemişse otomatik olarak Hugging Face base modeline döner.
    """
    model_config = get_model_config()

    base_model_name = model_config["base_model_name"]
    fine_tuned_model_path = model_config.get("fine_tuned_model_path")

    if fine_tuned_model_path:
        full_path: Path = get_project_root() / fine_tuned_model_path

        if full_path.exists() and full_path.is_dir():
            return str(full_path)

    return base_model_name


def load_embedding_model() -> SentenceTransformer:
    """
    Embedding modelini yükler.

    Öncelik:
    1. models/ecommerce-semantic-model gibi fine-tuned model klasörü
    2. config/model.yaml içindeki base_model_name
    """
    global _EMBEDDING_MODEL_CACHE

    if _EMBEDDING_MODEL_CACHE is not None:
        return _EMBEDDING_MODEL_CACHE

    model_path = resolve_model_path()
    model_config = get_model_config()
    device = model_config.get("device", "auto")

    if device == "auto":
        model = SentenceTransformer(model_path)
    else:
        model = SentenceTransformer(model_path, device=device)

    _EMBEDDING_MODEL_CACHE = model
    return _EMBEDDING_MODEL_CACHE


def clear_embedding_model_cache() -> None:
    """
    Test/debug senaryolarında cache'teki embedding modelini temizler.
    """
    global _EMBEDDING_MODEL_CACHE
    _EMBEDDING_MODEL_CACHE = None


def encode_text(model: SentenceTransformer, text: str) -> np.ndarray:
    """
    Tek bir metni embedding vektörüne çevirir.
    """
    model_config = get_model_config()
    normalize = model_config.get("normalize_embeddings", True)

    embedding = model.encode(
        text,
        normalize_embeddings=normalize,
        convert_to_numpy=True,
    )

    return embedding


def encode_texts(model: SentenceTransformer, texts: Iterable[str]) -> np.ndarray:
    """
    Birden fazla metni embedding vektörlerine çevirir.
    """
    model_config = get_model_config()
    normalize = model_config.get("normalize_embeddings", True)

    embeddings = model.encode(
        list(texts),
        normalize_embeddings=normalize,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return embeddings


def test_model() -> None:
    """
    Model yükleme ve embedding boyutu testidir.
    """
    model_config = get_model_config()
    expected_dim = model_config["embedding_dimension"]
    model_path = resolve_model_path()

    model = load_embedding_model()

    sample_text = "1000 TL altı stokta olan kablosuz kulaklık öner"
    embedding = encode_text(model, sample_text)

    print(f"Yüklenen model: {model_path}")
    print(f"Base model: {model_config['base_model_name']}")
    print(f"Örnek metin: {sample_text}")
    print(f"Embedding boyutu: {embedding.shape[0]}")

    if embedding.shape[0] != expected_dim:
        raise ValueError(
            f"Embedding boyutu beklenen değerle uyuşmuyor. "
            f"Beklenen: {expected_dim}, Gelen: {embedding.shape[0]}"
        )

    print("Embedding boyutu config ile uyumlu.")


if __name__ == "__main__":
    test_model()
