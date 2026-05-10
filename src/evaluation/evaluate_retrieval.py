import re
from dataclasses import dataclass, field
from typing import Any

from src.search.semantic_search import semantic_search


@dataclass
class RetrievalTestCase:
    query: str
    expected_table: str | None = None
    expected_brand: str | None = None
    expected_category: str | None = None
    expected_status: str | None = None
    expected_title_contains: str | None = None
    max_price: float | None = None
    min_price: float | None = None
    in_stock: bool | None = None
    out_of_stock: bool | None = None
    min_rating: int | None = None
    max_rating: int | None = None
    rating_equals: int | None = None
    expected_attribute_filters: dict[str, Any] | None = field(default_factory=dict)
    min_similarity_score: float | None = None


CATEGORY_EXPANSIONS = {
    "Ayakkabı": [
        "Ayakkabı",
        "Spor Ayakkabı",
        "Günlük Ayakkabı",
        "Koşu Ayakkabısı",
        "Bot",
    ],
    "Kulaklık": [
        "Kulaklık",
        "Oyuncu Kulaklığı",
        "Kablosuz Kulaklık",
    ],
    "Mouse": [
        "Mouse",
        "Oyuncu Mouse",
    ],
    "Telefon": [
        "Telefon",
        "Akıllı Telefon",
    ],
}


ATTRIBUTE_KEY_ALIASES = {
    "renk": ["renk"],
    "beden": ["beden"],
    "numara": ["numara"],
    "ram": ["ram"],
    "depolama": ["depolama"],
    "kapasite": ["kapasite"],
    "oyuncu": ["oyuncu"],
    "baglanti": ["baglanti", "bağlantı"],
    "yenileme_hizi": ["yenileme_hizi"],
    "ekran_boyutu": ["ekran_boyutu", "boyut", "ekran"],
    "kumas": ["kumas", "kumaş"],
}


TEST_CASES = [
    # A) Ürün arama testleri
    RetrievalTestCase(
        query="1000 TL altı stokta olan kablosuz kulaklık öner",
        expected_table="urun_varyantlari",
        expected_category="Kulaklık",
        max_price=1000,
        in_stock=True,
        expected_attribute_filters={"baglanti": "Bluetooth"},
    ),
    RetrievalTestCase(
        query="oyuncu mouse öner",
        expected_table="urun_varyantlari",
        expected_category="Mouse",
        expected_attribute_filters={"oyuncu": True},
    ),
    RetrievalTestCase(
        query="Samsung marka telefonları göster",
        expected_table="urun_varyantlari",
        expected_brand="samsung",
        expected_category="Telefon",
    ),
    RetrievalTestCase(
        query="iPhone 40000 TL altı telefon",
        expected_table="urun_varyantlari",
        expected_brand="apple",
        expected_category="Telefon",
        max_price=40000,
    ),
    RetrievalTestCase(
        query="10000 TL üstü telefon",
        expected_table="urun_varyantlari",
        expected_category="Telefon",
        min_price=10000,
    ),
    RetrievalTestCase(
        query="en ucuz laptop",
        expected_table="urun_varyantlari",
        expected_category="Laptop",
    ),
    RetrievalTestCase(
        query="en pahalı telefon",
        expected_table="urun_varyantlari",
        expected_category="Telefon",
    ),
    RetrievalTestCase(
        query="pahalı iphone",
        expected_table="urun_varyantlari",
        expected_brand="apple",
        expected_category="Telefon",
    ),
    RetrievalTestCase(
        query="stokta olmayan ürünleri listele",
        expected_table="urun_varyantlari",
        out_of_stock=True,
    ),

    # B) Giyim / varyant testleri
    RetrievalTestCase(
        query="s beden siyah tişört",
        expected_table="urun_varyantlari",
        expected_category="Tişört",
        expected_attribute_filters={"beden": "S", "renk": "Siyah"},
    ),
    RetrievalTestCase(
        query="m beden gri tişört",
        expected_table="urun_varyantlari",
        expected_category="Tişört",
        expected_attribute_filters={"beden": "M", "renk": "Gri"},
    ),
    RetrievalTestCase(
        query="l beden lacivert tişört",
        expected_table="urun_varyantlari",
        expected_category="Tişört",
        expected_attribute_filters={"beden": "L", "renk": "Lacivert"},
    ),
    RetrievalTestCase(
        query="xl beden beyaz tişört",
        expected_table="urun_varyantlari",
        expected_category="Tişört",
        expected_attribute_filters={"beden": "XL", "renk": "Beyaz"},
    ),
    RetrievalTestCase(
        query="kırmızı tişört",
        expected_table="urun_varyantlari",
        expected_category="Tişört",
        expected_attribute_filters={"renk": "Kırmızı"},
    ),
    RetrievalTestCase(
        query="bordo sweatshirt",
        expected_table="urun_varyantlari",
        expected_category="Sweatshirt",
        expected_attribute_filters={"renk": "Bordo"},
    ),
    RetrievalTestCase(
        query="bej sweatshirt",
        expected_table="urun_varyantlari",
        expected_category="Sweatshirt",
        expected_attribute_filters={"renk": "Bej"},
    ),
    RetrievalTestCase(
        query="haki sweatshirt",
        expected_table="urun_varyantlari",
        expected_category="Sweatshirt",
        expected_attribute_filters={"renk": "Haki"},
    ),
    RetrievalTestCase(
        query="lacivert gömlek",
        expected_table="urun_varyantlari",
        expected_category="Gömlek",
        expected_attribute_filters={"renk": "Lacivert"},
    ),
    RetrievalTestCase(
        query="gri pantolon",
        expected_table="urun_varyantlari",
        expected_category="Pantolon",
        expected_attribute_filters={"renk": "Gri"},
    ),
    RetrievalTestCase(
        query="32 beden mavi pantolon",
        expected_table="urun_varyantlari",
        expected_category="Pantolon",
        expected_attribute_filters={"beden": "32", "renk": "Mavi"},
    ),
    RetrievalTestCase(
        query="siyah xl mont",
        expected_table="urun_varyantlari",
        expected_category="Mont",
        expected_attribute_filters={"beden": "XL", "renk": "Siyah"},
    ),

    # C) Ayakkabı testleri
    RetrievalTestCase(
        query="42 numara ayakkabı",
        expected_table="urun_varyantlari",
        expected_category="Ayakkabı",
        expected_attribute_filters={"numara": "42"},
    ),
    RetrievalTestCase(
        query="koşu ayakkabısı öner",
        expected_table="urun_varyantlari",
        expected_category="Koşu Ayakkabısı",
    ),
    RetrievalTestCase(
        query="Nike ayakkabı yorumları",
        expected_table="urun_yorumlari",
        expected_brand="nike",
        expected_category="Ayakkabı",
    ),
    RetrievalTestCase(
        query="yüksek puanlı ayakkabı yorumları",
        expected_table="urun_yorumlari",
        expected_category="Ayakkabı",
        min_rating=4,
    ),

    # D) Teknoloji özellik testleri
    RetrievalTestCase(
        query="iphone 15 mavi",
        expected_table="urun_varyantlari",
        expected_brand="apple",
        expected_category="Telefon",
        expected_title_contains="iPhone 15",
        expected_attribute_filters={"renk": "Mavi"},
    ),
    RetrievalTestCase(
        query="samsung s23 gri",
        expected_table="urun_varyantlari",
        expected_brand="samsung",
        expected_category="Telefon",
        expected_title_contains="Galaxy S23",
        expected_attribute_filters={"renk": "Gri"},
    ),
    RetrievalTestCase(
        query="redmi note 13 pro",
        expected_table="urun_varyantlari",
        expected_brand="xiaomi",
        expected_category="Telefon",
        expected_title_contains="Redmi Note 13 Pro",
    ),
    RetrievalTestCase(
        query="poco x6 pro 512 gb",
        expected_table="urun_varyantlari",
        expected_brand="poco",
        expected_category="Telefon",
        expected_title_contains="Poco X6 Pro",
        expected_attribute_filters={"depolama": "512GB"},
    ),
    RetrievalTestCase(
        query="macbook air m2 8 gb",
        expected_table="urun_varyantlari",
        expected_brand="apple",
        expected_category="Laptop",
        expected_title_contains="MacBook Air M2",
        expected_attribute_filters={"ram": "8GB"},
    ),
    RetrievalTestCase(
        query="hp victus 16 oyuncu laptop",
        expected_table="urun_varyantlari",
        expected_brand="hp",
        expected_category="Laptop",
        expected_title_contains="Victus 16",
        expected_attribute_filters={"oyuncu": True},
    ),
    RetrievalTestCase(
        query="32 gb ram oyuncu laptop",
        expected_table="urun_varyantlari",
        expected_category="Laptop",
        expected_attribute_filters={"ram": "32GB", "oyuncu": True},
    ),
    RetrievalTestCase(
        query="pembe kulaklık",
        expected_table="urun_varyantlari",
        expected_category="Kulaklık",
        expected_attribute_filters={"renk": "Pembe"},
    ),

    # E) Yorum testleri
    RetrievalTestCase(
        query="iphone 11 yorumları",
        expected_table="urun_yorumlari",
        expected_brand="apple",
        expected_category="Telefon",
        expected_title_contains="iPhone 11",
    ),
    RetrievalTestCase(
        query="samsung s23 yorumları",
        expected_table="urun_yorumlari",
        expected_brand="samsung",
        expected_category="Telefon",
        expected_title_contains="Galaxy S23",
    ),
    RetrievalTestCase(
        query="macbook air m2 yorumları",
        expected_table="urun_yorumlari",
        expected_brand="apple",
        expected_category="Laptop",
        expected_title_contains="MacBook Air M2",
    ),
    RetrievalTestCase(
        query="düşük puanlı iphone yorumları",
        expected_table="urun_yorumlari",
        expected_brand="apple",
        expected_category="Telefon",
        max_rating=2,
    ),
    RetrievalTestCase(
        query="yüksek puanlı samsung yorumları",
        expected_table="urun_yorumlari",
        expected_brand="samsung",
        min_rating=4,
    ),
    RetrievalTestCase(
        query="kötü yorumlar",
        expected_table="urun_yorumlari",
        max_rating=2,
    ),
    RetrievalTestCase(
        query="olumsuz yorumlar",
        expected_table="urun_yorumlari",
        max_rating=2,
    ),
    RetrievalTestCase(
        query="1 yıldız yorumlar",
        expected_table="urun_yorumlari",
        rating_equals=1,
    ),
    RetrievalTestCase(
        query="3 puan altı yorumlar",
        expected_table="urun_yorumlari",
        max_rating=3,
    ),
    RetrievalTestCase(
        query="4 puan ve üzeri yorumlar",
        expected_table="urun_yorumlari",
        min_rating=4,
    ),

    # F) Kargo / iade testleri
    RetrievalTestCase(
        query="teslim edilen kargoları listele",
        expected_table="kargolar",
        expected_status="teslim_edildi",
    ),
    RetrievalTestCase(
        query="hasarlı gelen ürün iadelerini göster",
        expected_table="iadeler",
        expected_title_contains="İade",
    ),
]


def normalize_text(value: Any) -> str:
    """
    Karşılaştırmaları Türkçe/büyük-küçük harf ve boşluk farklarına daha dayanıklı yapar.
    """
    return " ".join(str(value).casefold().strip().split())


def normalize_compact(value: Any) -> str:
    """
    16 GB / 16GB gibi yazım farklarını eşitlemek için boşlukları kaldırır.
    """
    return normalize_text(value).replace(" ", "")


def normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    normalized = normalize_text(value)
    if normalized in {"true", "1", "evet", "var", "yes"}:
        return True
    if normalized in {"false", "0", "hayır", "hayir", "yok", "no"}:
        return False

    return None


def to_float(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", text):
        text = text.replace(".", "")

    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def to_int(value: Any) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def value_matches(actual: Any, expected: Any) -> bool:
    if isinstance(expected, bool):
        return normalize_bool(actual) is expected

    if isinstance(expected, (int, float)):
        actual_number = to_float(actual)
        return actual_number == float(expected)

    return normalize_compact(actual) == normalize_compact(expected)


def metadata_values(metadata: dict[str, Any], keys: list[str]) -> list[Any]:
    values: list[Any] = []

    for key in keys:
        value = metadata.get(key)
        if value is None:
            continue

        if isinstance(value, list):
            values.extend(value)
        else:
            values.append(value)

    return values


def get_category_values(metadata: dict[str, Any]) -> list[str]:
    category_values: list[str] = []

    for value in metadata_values(
        metadata,
        ["kategori", "ust_kategori", "kategoriler", "ust_kategoriler"],
    ):
        category_values.append(normalize_text(value))

    return category_values


def category_matches(metadata: dict[str, Any], expected_category: str) -> bool:
    actual_categories = set(get_category_values(metadata))
    expected_categories = CATEGORY_EXPANSIONS.get(expected_category, [expected_category])
    expected_categories_normalized = {normalize_text(category) for category in expected_categories}

    return bool(actual_categories & expected_categories_normalized)


def brand_matches(metadata: dict[str, Any], expected_brand: str) -> bool:
    actual_brand = metadata.get("marka")
    if actual_brand is None:
        return False

    return normalize_text(actual_brand) == normalize_text(expected_brand)


def status_matches(metadata: dict[str, Any], expected_status: str) -> bool:
    return normalize_text(metadata.get("durum")) == normalize_text(expected_status)


def title_matches(result: dict[str, Any], expected_title_contains: str) -> bool:
    haystack_parts = [
        result.get("baslik"),
        (result.get("metadata") or {}).get("urun_adi"),
        (result.get("metadata") or {}).get("urun"),
        (result.get("metadata") or {}).get("baslik"),
    ]
    haystack = " ".join(str(part) for part in haystack_parts if part)

    return normalize_text(expected_title_contains) in normalize_text(haystack)


def price_matches(metadata: dict[str, Any], test_case: RetrievalTestCase) -> bool:
    if test_case.min_price is None and test_case.max_price is None:
        return True

    price = to_float(metadata.get("satis_fiyati") or metadata.get("liste_fiyati"))
    if price is None:
        return False

    if test_case.min_price is not None and price < test_case.min_price:
        return False

    if test_case.max_price is not None and price > test_case.max_price:
        return False

    return True


def stock_matches(metadata: dict[str, Any], test_case: RetrievalTestCase) -> bool:
    if test_case.in_stock is None and test_case.out_of_stock is None:
        return True

    stock = to_int(metadata.get("stok"))
    if stock is None:
        return False

    if test_case.in_stock is True and stock <= 0:
        return False

    if test_case.out_of_stock is True and stock != 0:
        return False

    return True


def rating_matches(metadata: dict[str, Any], test_case: RetrievalTestCase) -> bool:
    if (
        test_case.min_rating is None
        and test_case.max_rating is None
        and test_case.rating_equals is None
    ):
        return True

    rating = to_int(metadata.get("puan"))
    if rating is None:
        return False

    if test_case.rating_equals is not None and rating != test_case.rating_equals:
        return False

    if test_case.min_rating is not None and rating < test_case.min_rating:
        return False

    if test_case.max_rating is not None and rating > test_case.max_rating:
        return False

    return True


def attribute_matches(metadata: dict[str, Any], expected_attributes: dict[str, Any]) -> bool:
    attributes = metadata.get("ozellikler") or {}
    if not isinstance(attributes, dict):
        return False

    for expected_key, expected_value in expected_attributes.items():
        aliases = ATTRIBUTE_KEY_ALIASES.get(expected_key, [expected_key])
        actual_values = metadata_values(attributes, aliases)

        if not actual_values:
            return False

        if not any(value_matches(actual_value, expected_value) for actual_value in actual_values):
            return False

    return True


def result_mismatch_reasons(
    result: dict[str, Any],
    test_case: RetrievalTestCase,
) -> list[str]:
    """
    Tek bir arama sonucunun hangi beklenen koşulları sağlamadığını döndürür.
    """
    reasons: list[str] = []
    metadata = result.get("metadata") or {}

    if test_case.expected_table is not None:
        if result.get("kaynak_tablo") != test_case.expected_table:
            reasons.append(
                f"tablo beklenen={test_case.expected_table}, gelen={result.get('kaynak_tablo')}"
            )

    if test_case.expected_brand is not None and not brand_matches(metadata, test_case.expected_brand):
        reasons.append(
            f"marka beklenen={test_case.expected_brand}, gelen={metadata.get('marka')}"
        )

    if test_case.expected_category is not None and not category_matches(
        metadata,
        test_case.expected_category,
    ):
        reasons.append(
            f"kategori beklenen={test_case.expected_category}, gelen={get_category_values(metadata)}"
        )

    if test_case.expected_status is not None and not status_matches(
        metadata,
        test_case.expected_status,
    ):
        reasons.append(
            f"durum beklenen={test_case.expected_status}, gelen={metadata.get('durum')}"
        )

    if test_case.expected_title_contains is not None and not title_matches(
        result,
        test_case.expected_title_contains,
    ):
        reasons.append(
            f"başlık beklenen içerik={test_case.expected_title_contains}, gelen={result.get('baslik')}"
        )

    if not price_matches(metadata, test_case):
        reasons.append(
            f"fiyat beklenen min={test_case.min_price}, max={test_case.max_price}, "
            f"gelen={metadata.get('satis_fiyati') or metadata.get('liste_fiyati')}"
        )

    if not stock_matches(metadata, test_case):
        reasons.append(
            f"stok beklenen in_stock={test_case.in_stock}, out_of_stock={test_case.out_of_stock}, "
            f"gelen={metadata.get('stok')}"
        )

    if not rating_matches(metadata, test_case):
        reasons.append(
            f"puan beklenen min={test_case.min_rating}, max={test_case.max_rating}, "
            f"eşit={test_case.rating_equals}, gelen={metadata.get('puan')}"
        )

    expected_attributes = test_case.expected_attribute_filters or {}
    if expected_attributes and not attribute_matches(metadata, expected_attributes):
        reasons.append(
            f"özellikler beklenen={expected_attributes}, gelen={metadata.get('ozellikler')}"
        )

    if test_case.min_similarity_score is not None:
        score = result.get("similarity_score")
        if score is None or score < test_case.min_similarity_score:
            reasons.append(
                f"skor beklenen>={test_case.min_similarity_score}, gelen={score}"
            )

    return reasons


def result_matches_test_case(result: dict[str, Any], test_case: RetrievalTestCase) -> bool:
    """
    Tek bir arama sonucunun beklenen metadata koşullarını sağlayıp sağlamadığını kontrol eder.
    """
    return not result_mismatch_reasons(result, test_case)


def describe_test_case(test_case: RetrievalTestCase) -> str:
    expected_parts = []

    for field_name in (
        "expected_table",
        "expected_brand",
        "expected_category",
        "expected_status",
        "expected_title_contains",
        "min_price",
        "max_price",
        "in_stock",
        "out_of_stock",
        "min_rating",
        "max_rating",
        "rating_equals",
        "expected_attribute_filters",
        "min_similarity_score",
    ):
        value = getattr(test_case, field_name)
        if value not in (None, {}, []):
            expected_parts.append(f"{field_name}={value}")

    return ", ".join(expected_parts) if expected_parts else "Koşul yok"


def evaluate_test_case(test_case: RetrievalTestCase, limit: int = 5) -> dict[str, Any]:
    """
    Bir test sorgusu için semantic search çalıştırır ve Top-1 / Top-K başarısını döndürür.
    """
    print("\n" + "=" * 80)
    print(f"SORGU: {test_case.query}")
    print("=" * 80)

    results = semantic_search(test_case.query, limit=limit)

    top_1_success = False
    top_k_success = False
    top_1_mismatch_reasons: list[str] = []

    if results:
        top_1_mismatch_reasons = result_mismatch_reasons(results[0], test_case)
        top_1_success = not top_1_mismatch_reasons
        top_k_success = any(result_matches_test_case(result, test_case) for result in results)

    print(f"Beklenen koşullar: {describe_test_case(test_case)}")
    print(f"Top-1 başarılı mı: {top_1_success}")
    print(f"Top-{limit} başarılı mı: {top_k_success}")

    if results:
        print("\nİlk sonuç:")
        print(f"  Tablo : {results[0]['kaynak_tablo']}")
        print(f"  Başlık: {results[0]['baslik']}")
        print(f"  Skor  : {results[0]['similarity_score']:.4f}")

        if top_1_mismatch_reasons:
            print("  Top-1 uyumsuzlukları:")
            for reason in top_1_mismatch_reasons:
                print(f"    - {reason}")
    else:
        print("Sonuç bulunamadı.")

    return {
        "query": test_case.query,
        "expected": describe_test_case(test_case),
        "top_1_success": top_1_success,
        "top_k_success": top_k_success,
        "result_count": len(results),
        "top_1_title": results[0]["baslik"] if results else None,
        "top_1_table": results[0]["kaynak_tablo"] if results else None,
        "top_1_score": results[0]["similarity_score"] if results else None,
        "top_1_mismatch_reasons": top_1_mismatch_reasons,
    }


def evaluate_all(limit: int = 5) -> None:
    """
    Tüm test sorguları için retrieval değerlendirmesi yapar.
    """
    evaluation_results = []

    for test_case in TEST_CASES:
        result = evaluate_test_case(test_case, limit=limit)
        evaluation_results.append(result)

    total = len(evaluation_results)
    top_1_correct = sum(1 for result in evaluation_results if result["top_1_success"])
    top_k_correct = sum(1 for result in evaluation_results if result["top_k_success"])

    top_1_accuracy = top_1_correct / total if total else 0
    top_k_accuracy = top_k_correct / total if total else 0

    print("\n" + "#" * 80)
    print("GENEL DEĞERLENDİRME")
    print("#" * 80)
    print(f"Test sorgusu sayısı : {total}")
    print(f"Top-1 doğru         : {top_1_correct}/{total}")
    print(f"Top-{limit} doğru       : {top_k_correct}/{total}")
    print(f"Top-1 Accuracy      : {top_1_accuracy:.4f}")
    print(f"Top-{limit} Accuracy    : {top_k_accuracy:.4f}")

    print("\nÖzet tablo:")
    for result in evaluation_results:
        status = "OK" if result["top_1_success"] else "FAIL"
        score = result["top_1_score"]
        score_text = f"{score:.4f}" if score is not None else "Yok"
        print(
            f"{status} | {result['query']} | "
            f"Top-1: {result['top_1_title']} | "
            f"Skor: {score_text}"
        )


if __name__ == "__main__":
    evaluate_all(limit=5)
