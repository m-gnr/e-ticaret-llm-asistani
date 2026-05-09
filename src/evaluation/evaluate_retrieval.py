from dataclasses import dataclass
from typing import Any

from src.search.semantic_search import semantic_search


@dataclass
class RetrievalTestCase:
    query: str
    expected_table: str
    expected_title_contains: str | None = None
    expected_status: str | None = None
    expected_category: str | None = None
    min_expected_score: float | None = None


TEST_CASES = [
    RetrievalTestCase(
        query="1000 TL altı stokta olan kablosuz kulaklık öner",
        expected_table="urun_varyantlari",
        expected_title_contains="Sony WH-CH520",
    ),
    RetrievalTestCase(
        query="oyuncu mouse öner",
        expected_table="urun_varyantlari",
        expected_title_contains="Razer DeathAdder",
    ),
    RetrievalTestCase(
        query="Samsung marka telefonları göster",
        expected_table="urun_varyantlari",
        expected_title_contains="Samsung Galaxy A55",
    ),
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
    RetrievalTestCase(
        query="yüksek puanlı ayakkabı yorumları",
        expected_table="urun_yorumlari",
        expected_category="Ayakkabı",
    ),
    RetrievalTestCase(
        query="en az 4 puan alan ayakkabı yorumları",
        expected_table="urun_yorumlari",
        expected_category="Ayakkabı",
    ),
    RetrievalTestCase(
        query="stokta olmayan ürünleri listele",
        expected_table="urun_varyantlari",
    ),
]


def result_matches_test_case(result: dict[str, Any], test_case: RetrievalTestCase) -> bool:
    """
    Tek bir arama sonucunun beklenen koşulları sağlayıp sağlamadığını kontrol eder.
    """
    if result["kaynak_tablo"] != test_case.expected_table:
        return False

    if test_case.expected_title_contains is not None:
        title = result["baslik"] or ""
        if test_case.expected_title_contains.lower() not in title.lower():
            return False

    metadata = result.get("metadata") or {}

    if test_case.expected_status is not None:
        if metadata.get("durum") != test_case.expected_status:
            return False

    if test_case.expected_category is not None:
        kategoriler = metadata.get("kategoriler", [])
        ust_kategoriler = metadata.get("ust_kategoriler", [])

        if (
            test_case.expected_category not in kategoriler
            and test_case.expected_category not in ust_kategoriler
        ):
            return False

    if test_case.min_expected_score is not None:
        if result["similarity_score"] < test_case.min_expected_score:
            return False

    return True


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

    if results:
        top_1_success = result_matches_test_case(results[0], test_case)
        top_k_success = any(result_matches_test_case(result, test_case) for result in results)

    print(f"Beklenen tablo: {test_case.expected_table}")
    print(f"Top-1 başarılı mı: {top_1_success}")
    print(f"Top-{limit} başarılı mı: {top_k_success}")

    if results:
        print("\nİlk sonuç:")
        print(f"  Tablo : {results[0]['kaynak_tablo']}")
        print(f"  Başlık: {results[0]['baslik']}")
        print(f"  Skor  : {results[0]['similarity_score']:.4f}")
    else:
        print("Sonuç bulunamadı.")

    return {
        "query": test_case.query,
        "expected_table": test_case.expected_table,
        "top_1_success": top_1_success,
        "top_k_success": top_k_success,
        "result_count": len(results),
        "top_1_title": results[0]["baslik"] if results else None,
        "top_1_table": results[0]["kaynak_tablo"] if results else None,
        "top_1_score": results[0]["similarity_score"] if results else None,
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
        status = "✅" if result["top_1_success"] else "❌"
        print(
            f"{status} | {result['query']} | "
            f"Top-1: {result['top_1_title']} | "
            f"Skor: {result['top_1_score']}"
        )


if __name__ == "__main__":
    evaluate_all(limit=5)