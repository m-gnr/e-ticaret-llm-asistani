from src.app.answer_generator import generate_answer
from src.search.query_parser import parse_query
from src.search.semantic_search import semantic_search


def print_header() -> None:
    """
    CLI uygulaması başlangıç ekranı.
    """
    print("=" * 80)
    print("E-TİCARET LLM ASİSTANI")
    print("=" * 80)
    print("Doğal dil ile e-ticaret veritabanında arama yapabilirsiniz.")
    print("Çıkmak için: q, quit, exit")
    print("-" * 80)
    print("Örnek sorgular:")
    print("- 1000 TL altı stokta olan kablosuz kulaklık öner")
    print("- teslim edilen kargoları listele")
    print("- yüksek puanlı ayakkabı yorumları")
    print("- Samsung marka telefonları göster")
    print("- hasarlı gelen ürün iadelerini göster")
    print("=" * 80)


def print_parsed_query(parsed_query) -> None:
    """
    Query parser çıktısını terminalde okunabilir gösterir.
    """
    print("\nSORGUNUN ANALİZİ")
    print("-" * 80)
    print(f"Orijinal sorgu      : {parsed_query.original_query}")
    print(f"Arama metni         : {parsed_query.search_text}")
    print(f"Amaç / intent       : {parsed_query.intent}")
    print(f"Kaynak tablolar     : {parsed_query.source_tables}")
    print(f"Maksimum fiyat      : {parsed_query.max_price}")
    print(f"Minimum fiyat       : {parsed_query.min_price}")
    print(f"Stokta olanlar      : {parsed_query.in_stock_only}")
    print(f"Stokta olmayanlar   : {parsed_query.out_of_stock_only}")
    print(f"Minimum puan        : {parsed_query.min_rating}")
    print(f"Kategori            : {parsed_query.category}")
    print(f"Marka               : {parsed_query.brand}")
    print(f"Durum               : {parsed_query.status}")


def print_raw_results(results: list[dict], max_content_length: int = 300) -> None:
    """
    Ham semantic search sonuçlarını kısa biçimde gösterir.
    """
    print("\nKAYNAK SONUÇLAR")
    print("-" * 80)

    if not results:
        print("Sonuç bulunamadı.")
        return

    for index, result in enumerate(results, start=1):
        print(f"{index}. {result.get('baslik')}")
        print(f"   Kaynak tablo : {result.get('kaynak_tablo')}")
        print(f"   Benzerlik    : {result.get('similarity_score'):.4f}")

        content = result.get("icerik", "")
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        print(f"   İçerik       : {content}")
        print()


def handle_query(query: str, limit: int = 5, show_debug: bool = True) -> None:
    """
    Tek bir kullanıcı sorgusunu işler.

    Akış:
    1. Sorguyu parse eder.
    2. Semantic search çalıştırır.
    3. Doğal dil cevabı üretir.
    4. İsteğe bağlı debug bilgilerini gösterir.
    """
    parsed_query = parse_query(query)
    results = semantic_search(query, limit=limit)

    answer = generate_answer(
        query=query,
        results=results,
        parsed_query=parsed_query,
    )

    print("\nASİSTAN CEVABI")
    print("=" * 80)
    print(answer)

    if show_debug:
        print_parsed_query(parsed_query)
        print_raw_results(results)


def run_cli() -> None:
    """
    Terminal tabanlı demo uygulaması.
    """
    print_header()

    while True:
        query = input("\nSorgu giriniz: ").strip()

        if query.lower() in {"q", "quit", "exit", "çık", "cik"}:
            print("Uygulama kapatılıyor.")
            break

        if not query:
            print("Lütfen boş olmayan bir sorgu giriniz.")
            continue

        try:
            handle_query(query=query, limit=5, show_debug=True)
        except Exception as error:
            print("\nBir hata oluştu:")
            print(error)


if __name__ == "__main__":
    run_cli()