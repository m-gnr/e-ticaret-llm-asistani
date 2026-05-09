from typing import Any

from pgvector.psycopg import Vector

from src.config_loader import load_yaml_config
from src.database.db import get_db_connection
from src.embedding.model_loader import encode_text, load_embedding_model
from src.search.query_parser import ParsedQuery, parse_query


def get_search_config() -> dict[str, Any]:
    """
    config/search.yaml dosyasındaki arama ayarlarını okur.
    """
    config = load_yaml_config("config/search.yaml")
    return config["search"]


def build_filter_conditions(parsed_query: ParsedQuery) -> tuple[list[str], dict[str, Any]]:
    """
    ParsedQuery sonucuna göre SQL WHERE koşullarını ve parametreleri üretir.
    """
    conditions: list[str] = ["embedding IS NOT NULL"]
    params: dict[str, Any] = {}

    if parsed_query.source_tables:
        conditions.append("kaynak_tablo = ANY(%(source_tables)s)")
        params["source_tables"] = parsed_query.source_tables

    if parsed_query.max_price is not None:
        conditions.append("(metadata->>'satis_fiyati')::numeric <= %(max_price)s")
        params["max_price"] = parsed_query.max_price

    if parsed_query.min_price is not None:
        conditions.append("(metadata->>'satis_fiyati')::numeric >= %(min_price)s")
        params["min_price"] = parsed_query.min_price

    if parsed_query.in_stock_only:
        conditions.append("(metadata->>'stok')::integer > 0")

    if parsed_query.out_of_stock_only:
        conditions.append("(metadata->>'stok')::integer = 0")

    if parsed_query.min_rating is not None:
        conditions.append("(metadata->>'puan')::integer >= %(min_rating)s")
        params["min_rating"] = parsed_query.min_rating

    if parsed_query.brand is not None:
        conditions.append("LOWER(metadata->>'marka') = %(brand)s")
        params["brand"] = parsed_query.brand.lower()

    if parsed_query.category is not None:
        conditions.append(
            """
            (
                metadata->'kategoriler' ? %(category)s
                OR metadata->'ust_kategoriler' ? %(category)s
                OR metadata->>'kategori' = %(category)s
            )
            """
        )
        params["category"] = parsed_query.category

    if parsed_query.status is not None:
        conditions.append("metadata->>'durum' = %(status)s")
        params["status"] = parsed_query.status

    return conditions, params


def semantic_search(query_text: str, limit: int | None = None) -> list[dict[str, Any]]:
    """
    Kullanıcı sorgusunu parse eder, embedding'e çevirir ve semantic_index tablosunda
    filtreli semantik arama yapar.
    """
    search_config = get_search_config()

    if limit is None:
        limit = search_config.get("default_limit", 5)

    max_limit = search_config.get("max_limit", 20)
    limit = min(limit, max_limit)

    parsed_query = parse_query(query_text)

    embedding_text = parsed_query.search_text or parsed_query.original_query

    print("Parsed query:")
    print(parsed_query.to_dict())

    print("Embedding modeli yükleniyor...")
    model = load_embedding_model()

    print("Sorgu embedding'e çevriliyor...")
    query_embedding = encode_text(model, embedding_text)

    conditions, filter_params = build_filter_conditions(parsed_query)
    where_sql = " AND ".join(conditions)

    sql = f"""
        SELECT
            kaynak_tablo,
            kaynak_id,
            baslik,
            icerik,
            metadata,
            embedding <=> %(query_embedding)s AS distance
        FROM public.semantic_index
        WHERE {where_sql}
        ORDER BY embedding <=> %(query_embedding)s
        LIMIT %(limit)s;
    """

    params = {
        "query_embedding": Vector(query_embedding.tolist()),
        "limit": limit,
        **filter_params,
    }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

    results: list[dict[str, Any]] = []

    for row in rows:
        distance = float(row[5])
        similarity_score = 1 - distance

        results.append(
            {
                "kaynak_tablo": row[0],
                "kaynak_id": row[1],
                "baslik": row[2],
                "icerik": row[3],
                "metadata": row[4],
                "distance": distance,
                "similarity_score": similarity_score,
            }
        )

    return results


def print_search_results(results: list[dict[str, Any]]) -> None:
    """
    Semantic search sonuçlarını terminalde okunabilir şekilde gösterir.
    """
    if not results:
        print("Sonuç bulunamadı.")
        return

    for index, result in enumerate(results, start=1):
        print("=" * 80)
        print(f"{index}. Sonuç")
        print(f"Kaynak tablo     : {result['kaynak_tablo']}")
        print(f"Başlık           : {result['baslik']}")
        print(f"Similarity score : {result['similarity_score']:.4f}")
        print(f"Distance         : {result['distance']:.4f}")
        print("-" * 80)
        print(result["icerik"][:700])


def run_demo() -> None:
    """
    Terminalden hızlı filtreli semantic search testi yapar.
    """
    test_queries = [
        "1000 TL altı stokta olan kablosuz kulaklık öner",
        "hasarlı gelen ürün iadelerini göster",
        "teslim edilen kargoları listele",
        "oyuncu mouse öner",
        "yüksek puanlı ayakkabı yorumları",
        "Samsung marka telefonları göster",
        "stokta olmayan ürünleri listele",
        "en az 4 puan alan ayakkabı yorumları",
    ]

    for query in test_queries:
        print("\n\n")
        print("#" * 80)
        print(f"SORGU: {query}")
        print("#" * 80)

        results = semantic_search(query)
        print_search_results(results)


if __name__ == "__main__":
    run_demo()