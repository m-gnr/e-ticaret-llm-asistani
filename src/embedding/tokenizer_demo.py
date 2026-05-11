import json
from functools import lru_cache
from typing import Any

from transformers import AutoTokenizer, PreTrainedTokenizerBase

from src.config_loader import load_yaml_config
from src.embedding.model_loader import get_model_config, resolve_model_path


def get_tokenizer_config() -> dict[str, Any]:
    """
    config/model.yaml içindeki tokenizer ayarlarını okur.
    """
    config = load_yaml_config("config/model.yaml")
    return config.get("tokenizer", {})


@lru_cache(maxsize=1)
def load_tokenizer() -> PreTrainedTokenizerBase:
    """
    Fine-tuned model klasörü varsa onun tokenizer'ını, yoksa base model tokenizer'ını yükler.
    """
    model_path = resolve_model_path()
    return AutoTokenizer.from_pretrained(model_path)


def analyze_tokenization(text: str) -> dict[str, Any]:
    """
    Verilen metnin token, token id, attention mask ve padding bilgisini çıkarır.
    """
    tokenizer_config = get_tokenizer_config()
    model_config = get_model_config()
    tokenizer = load_tokenizer()

    max_length = int(tokenizer_config.get("max_length", 128))
    padding = tokenizer_config.get("padding", "max_length")
    truncation = bool(tokenizer_config.get("truncation", True))

    encoded = tokenizer(
        text or "",
        padding=padding,
        truncation=truncation,
        max_length=max_length,
        return_attention_mask=True,
        return_special_tokens_mask=True,
    )

    input_ids = list(encoded.get("input_ids", []))
    attention_mask = list(encoded.get("attention_mask", []))
    tokens = tokenizer.convert_ids_to_tokens(input_ids)
    token_type_ids = encoded.get("token_type_ids")
    special_tokens_mask = encoded.get("special_tokens_mask")

    unk_token = tokenizer.unk_token
    unk_token_count = (
        sum(1 for token in tokens if token == unk_token)
        if unk_token is not None
        else 0
    )

    return {
        "text": text or "",
        "tokens": tokens,
        "token_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": list(token_type_ids) if token_type_ids is not None else None,
        "special_tokens_mask": (
            list(special_tokens_mask) if special_tokens_mask is not None else None
        ),
        "vocab_size": tokenizer.vocab_size,
        "max_length": max_length,
        "padding": padding,
        "truncation": truncation,
        "real_token_count": sum(1 for value in attention_mask if value == 1),
        "padding_token_count": sum(1 for value in attention_mask if value == 0),
        "unk_token_count": unk_token_count,
        "cls_token": tokenizer.cls_token,
        "sep_token": tokenizer.sep_token,
        "pad_token": tokenizer.pad_token,
        "unk_token": tokenizer.unk_token,
        "tokenizer_source": resolve_model_path(),
        "base_model_name": model_config.get("base_model_name"),
        "fine_tuned_model_path": model_config.get("fine_tuned_model_path"),
    }


def run_demo() -> None:
    sample = "1000 TL altı stokta olan kablosuz kulaklık öner"
    result = analyze_tokenization(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_demo()
