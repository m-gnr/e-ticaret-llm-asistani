from pprint import pprint

from transformers import AutoTokenizer

from src.config_loader import load_yaml_config


def get_model_name() -> str:
    """
    Tokenizer, model.yaml içindeki base_model_name değerinden yüklenir.
    Böylece model adı hard-coded olmaz.
    """
    config = load_yaml_config("config/model.yaml")
    return config["model"]["base_model_name"]


def load_tokenizer():
    """
    Hugging Face tokenizer yükler.
    Tokenizer, metni modelin anlayacağı token ID dizisine çevirir.
    """
    model_name = get_model_name()
    return AutoTokenizer.from_pretrained(model_name)


def explain_tokenization(text: str, max_length: int = 32) -> None:
    """
    Bir metnin tokenizer tarafından nasıl işlendiğini gösterir.

    Gösterilen kavramlar:
    - tokenization
    - token
    - vocabulary / sözlük
    - token id
    - attention mask
    - padding
    - truncation
    """
    tokenizer = load_tokenizer()

    print("=" * 80)
    print("ORİJİNAL METİN")
    print("=" * 80)
    print(text)

    print("\n" + "=" * 80)
    print("1. TOKENIZATION")
    print("=" * 80)

    tokens = tokenizer.tokenize(text)
    print(tokens)

    print("\nAçıklama:")
    print(
        "Tokenization, metni modelin işleyebileceği küçük parçalara ayırma işlemidir. "
        "Bu parçalar kelime, kelime parçası veya özel sembol olabilir."
    )

    print("\n" + "=" * 80)
    print("2. TOKEN ID")
    print("=" * 80)

    token_ids_without_special = tokenizer.convert_tokens_to_ids(tokens)
    print(token_ids_without_special)

    print("\nAçıklama:")
    print(
        "Model doğrudan kelimeleri değil, sayıları işler. "
        "Her token, tokenizer sözlüğündeki bir ID değerine karşılık gelir."
    )

    print("\n" + "=" * 80)
    print("3. MODEL INPUT")
    print("=" * 80)

    encoded = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors=None,
    )

    pprint(encoded)

    print("\nAçıklama:")
    print("input_ids      → Modele verilen token ID dizisidir.")
    print("attention_mask → 1 olan yerler gerçek token, 0 olan yerler padding alanıdır.")
    print("padding        → Kısa metinleri aynı uzunluğa tamamlamak için eklenen boş tokenlardır.")
    print("truncation     → Uzun metinleri max_length sınırına göre kesme işlemidir.")

    print("\n" + "=" * 80)
    print("4. INPUT IDS → TOKEN GERİ DÖNÜŞÜMÜ")
    print("=" * 80)

    decoded_tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
    print(decoded_tokens)

    print("\nAçıklama:")
    print(
        "Bu çıktı, input_ids içindeki sayıların tekrar hangi tokenlara karşılık "
        "geldiğini gösterir. Bu modelde <s>, </s>, <pad> gibi özel tokenlar görülebilir."
    )

    print("\n" + "=" * 80)
    print("5. VOCABULARY / SÖZLÜK ÖRNEĞİ")
    print("=" * 80)

    vocab = tokenizer.get_vocab()
    sample_items = list(vocab.items())[:20]

    print("Sözlük boyutu:", len(vocab))
    print("İlk 20 sözlük elemanı:")
    pprint(sample_items)

    print("\nAçıklama:")
    print(
        "Vocabulary yani sözlük, tokenların sayısal ID karşılıklarını tutar. "
        "Modelin bildiği tokenlar bu sözlükte yer alır."
    )


def run_demo() -> None:
    sample_queries = [
        "1000 TL altı stokta olan kablosuz kulaklık öner",
        "hasarlı gelen ürün iadelerini göster",
        "yüksek puanlı ayakkabı yorumları",
    ]

    for query in sample_queries:
        explain_tokenization(query)
        print("\n\n")


if __name__ == "__main__":
    run_demo()