from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config_loader import load_yaml_config


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


def load_embedding_model() -> SentenceTransformer:
    """
    Embedding modelini config dosyasındaki base_model_name değerine göre yükler.

    Fine-tuning sonrası istersek burada fine_tuned_model_path kullanılabilir.
    """
    model_config = get_model_config()
    model_name = model_config["base_model_name"]
    device = model_config.get("device", "auto")

    if device == "auto":
        model = SentenceTransformer(model_name)
    else:
        model = SentenceTransformer(model_name, device=device)

    return model


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

    model = load_embedding_model()

    sample_text = "1000 TL altı stokta olan kablosuz kulaklık öner"
    embedding = encode_text(model, sample_text)

    print(f"Model başarıyla yüklendi: {model_config['base_model_name']}")
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