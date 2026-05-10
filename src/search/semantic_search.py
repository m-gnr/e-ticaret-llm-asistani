from typing import Any

from pgvector.psycopg import Vector

from src.config_loader import load_yaml_config
from src.database.db import get_db_connection
from src.embedding.model_loader import encode_text, load_embedding_model
from src.search.query_parser import ParsedQuery, parse_query


ATTRIBUTE_KEY_MAP = {
    "depolama": "depolama",
    "ram": "ram",
    "baglanti": "baglanti",
    "renk": "renk",
    "yenileme_hizi": "yenileme_hizi",
    "ekran_boyutu": "boyut",
    "kapasite": "kapasite",
    "oyuncu": "oyuncu",
    "beden": "beden",
    "numara": "numara",
    "kumas": "kumas",
}


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


def get_search_config() -> dict[str, Any]:
    """
    config/search.yaml dosyasındaki arama ayarlarını okur.
    """
    config = load_yaml_config("config/search.yaml")
    return config["search"]


def expand_category_values(category: str) -> list[str]:
    """
    Üst kategori sorgularını ilgili alt kategorilerle birlikte aramaya hazırlar.
    """
    return CATEGORY_EXPANSIONS.get(category, [category])


def has_exact_lookup_filter(parsed_query: ParsedQuery) -> bool:
    return any(
        [
            parsed_query.order_no,
            parsed_query.tracking_no,
            parsed_query.coupon_code,
        ]
    )


def build_filter_conditions(
    parsed_query: ParsedQuery,
    search_config: dict[str, Any] | None = None,
    fallback_level: int = 0,
) -> tuple[list[str], dict[str, Any]]:
    """
    ParsedQuery sonucuna göre SQL WHERE koşullarını ve parametreleri üretir.
    """
    if search_config is None:
        search_config = {}

    conditions: list[str] = ["embedding IS NOT NULL"]
    params: dict[str, Any] = {}
    exact_lookup = has_exact_lookup_filter(parsed_query)
    keep_source_tables = (
        fallback_level < 2
        or search_config.get("fallback_keep_source_tables", True)
        or exact_lookup
    )
    keep_model_filter = (
        fallback_level < 2
        or search_config.get("fallback_keep_model_filter", True)
        or exact_lookup
    )
    relax_attributes = (
        fallback_level >= 1
        and search_config.get("fallback_relax_attributes", True)
        and not exact_lookup
    )
    relax_price_stock = (
        fallback_level >= 1
        and search_config.get("fallback_relax_price_stock", False)
        and not exact_lookup
    )
    minimal_filters = fallback_level >= 2 and not exact_lookup

    if parsed_query.source_tables and keep_source_tables:
        conditions.append("kaynak_tablo = ANY(%(source_tables)s)")
        params["source_tables"] = parsed_query.source_tables

    if parsed_query.order_no is not None:
        conditions.append("LOWER(metadata->>'siparis_no') = LOWER(%(order_no)s)")
        params["order_no"] = parsed_query.order_no

    if parsed_query.tracking_no is not None:
        conditions.append("LOWER(metadata->>'takip_no') = LOWER(%(tracking_no)s)")
        params["tracking_no"] = parsed_query.tracking_no

    if parsed_query.coupon_code is not None:
        conditions.append("LOWER(metadata->>'kod') = LOWER(%(coupon_code)s)")
        params["coupon_code"] = parsed_query.coupon_code

    if exact_lookup:
        return conditions, params

    if parsed_query.max_price is not None and not relax_price_stock and not minimal_filters:
        conditions.append("(metadata->>'satis_fiyati')::numeric <= %(max_price)s")
        params["max_price"] = parsed_query.max_price

    if parsed_query.min_price is not None and not relax_price_stock and not minimal_filters:
        conditions.append("(metadata->>'satis_fiyati')::numeric >= %(min_price)s")
        params["min_price"] = parsed_query.min_price

    if parsed_query.in_stock_only and not relax_price_stock and not minimal_filters:
        conditions.append("(metadata->>'stok')::integer > 0")

    if parsed_query.out_of_stock_only and not relax_price_stock and not minimal_filters:
        conditions.append("(metadata->>'stok')::integer = 0")

    if parsed_query.min_rating is not None and not minimal_filters:
        conditions.append("(metadata->>'puan')::integer >= %(min_rating)s")
        params["min_rating"] = parsed_query.min_rating

    if parsed_query.max_rating is not None and not minimal_filters:
        conditions.append("(metadata->>'puan')::integer <= %(max_rating)s")
        params["max_rating"] = parsed_query.max_rating

    if parsed_query.rating_equals is not None and not minimal_filters:
        conditions.append("(metadata->>'puan')::integer = %(rating_equals)s")
        params["rating_equals"] = parsed_query.rating_equals

    if parsed_query.brand is not None and not minimal_filters:
        conditions.append("LOWER(metadata->>'marka') = %(brand)s")
        params["brand"] = parsed_query.brand.lower()

    if parsed_query.category is not None and not minimal_filters:
        category_values = expand_category_values(parsed_query.category)
        category_values_lower = [category.lower() for category in category_values]

        conditions.append(
            """
            (
                LOWER(metadata->>'kategori') = ANY(%(category_values_lower)s::text[])
                OR LOWER(metadata->>'ust_kategori') = ANY(%(category_values_lower)s::text[])
                OR EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements_text(
                        COALESCE(metadata->'kategoriler', '[]'::jsonb)
                    ) AS kategori_adi
                    WHERE LOWER(kategori_adi) = ANY(%(category_values_lower)s::text[])
                )
                OR EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements_text(
                        COALESCE(metadata->'ust_kategoriler', '[]'::jsonb)
                    ) AS ust_kategori_adi
                    WHERE LOWER(ust_kategori_adi) = ANY(%(category_values_lower)s::text[])
                )
            )
            """
        )
        params["category_values_lower"] = category_values_lower

    if parsed_query.status is not None and not minimal_filters:
        conditions.append("metadata->>'durum' = %(status)s")
        params["status"] = parsed_query.status

    if parsed_query.model_filter is not None and keep_model_filter:
        conditions.append(
            """
            (
                LOWER(baslik) LIKE LOWER(%(model_filter)s)
                OR LOWER(icerik) LIKE LOWER(%(model_filter)s)
                OR LOWER(metadata->>'urun_adi') LIKE LOWER(%(model_filter)s)
                OR LOWER(metadata->>'urun') LIKE LOWER(%(model_filter)s)
                OR LOWER(metadata->>'baslik') LIKE LOWER(%(model_filter)s)
                OR LOWER(metadata::text) LIKE LOWER(%(model_filter)s)
            )
            """
        )
        params["model_filter"] = f"%{parsed_query.model_filter}%"

    if relax_attributes or minimal_filters:
        return conditions, params

    for key, value in parsed_query.attribute_filters.items():
        metadata_key = ATTRIBUTE_KEY_MAP.get(key)
        if metadata_key is None:
            continue

        param_name = f"attr_{key}"
        metadata_expression = f"metadata->'ozellikler'->>'{metadata_key}'"

        if isinstance(value, bool):
            conditions.append(f"{metadata_expression} = %({param_name})s")
            params[param_name] = "true" if value else "false"
        else:
            conditions.append(f"LOWER({metadata_expression}) = LOWER(%({param_name})s)")
            params[param_name] = str(value)

    return conditions, params


def run_semantic_query(
    query_embedding: Any,
    parsed_query: ParsedQuery,
    limit: int,
    search_config: dict[str, Any],
    fallback_level: int = 0,
) -> list[dict[str, Any]]:
    conditions, filter_params = build_filter_conditions(
        parsed_query,
        search_config=search_config,
        fallback_level=fallback_level,
    )
    where_sql = " AND ".join(conditions)
    order_by_sql = build_order_by_clause(parsed_query)

    sql = f"""
        SELECT
            kaynak_tablo,
            kaynak_id,
            baslik,
            icerik,
            metadata,
            embedding <=> %(query_embedding)s AS distance,
            NULLIF(metadata->>'satis_fiyati', '')::numeric AS price,
            NULLIF(metadata->>'puan', '')::integer AS rating
        FROM public.semantic_index
        WHERE {where_sql}
        ORDER BY {order_by_sql}
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
                "used_fallback": fallback_level > 0,
            }
        )

    return results


def build_order_by_clause(parsed_query: ParsedQuery) -> str:
    if parsed_query.sort_by == "price":
        direction = "DESC" if parsed_query.sort_direction == "desc" else "ASC"
        return f"price {direction} NULLS LAST, distance ASC"

    if parsed_query.sort_by == "rating":
        direction = "DESC" if parsed_query.sort_direction == "desc" else "ASC"
        return f"rating {direction} NULLS LAST, distance ASC"

    return "distance ASC"


def semantic_search(
    query_text: str,
    limit: int | None = None,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """
    Kullanıcı sorgusunu parse eder, embedding'e çevirir ve semantic_index tablosunda
    filtreli semantik arama yapar.

    verbose=True verilirse ara adımları terminale yazdırır.
    """
    search_config = get_search_config()

    if limit is None:
        limit = search_config.get("default_limit", 5)

    max_limit = search_config.get("max_limit", 20)
    limit = min(limit, max_limit)

    parsed_query = parse_query(query_text)
    embedding_text = parsed_query.search_text or parsed_query.original_query

    if verbose:
        print("Parsed query:")
        print(parsed_query.to_dict())

    if verbose:
        print("Embedding modeli yükleniyor...")

    model = load_embedding_model()

    if verbose:
        print("Sorgu embedding'e çevriliyor...")

    query_embedding = encode_text(model, embedding_text)

    results = run_semantic_query(
        query_embedding=query_embedding,
        parsed_query=parsed_query,
        limit=limit,
        search_config=search_config,
        fallback_level=0,
    )
    if results:
        return results

    if (
        not search_config.get("enable_fallback_search", True)
        or has_exact_lookup_filter(parsed_query)
    ):
        return results

    if verbose:
        print("Strict filtreler sonuç döndürmedi, fallback arama deneniyor...")

    for fallback_level in (1, 2):
        results = run_semantic_query(
            query_embedding=query_embedding,
            parsed_query=parsed_query,
            limit=limit,
            search_config=search_config,
            fallback_level=fallback_level,
        )
        if results:
            return results

    return []


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
        "s beden siyah tişört",
        "m beden gri tişört",
        "l beden lacivert tişört",
        "xl beden beyaz tişört",
        "kırmızı tişört",
        "yeşil tişört",
        "bordo sweatshirt",
        "bej sweatshirt",
        "haki sweatshirt",
        "lacivert gömlek",
        "gri pantolon",
        "32 beden mavi pantolon",
        "haki mont",
        "siyah xl mont",
        "42 numara ayakkabı",
        "iphone 15 mavi",
        "samsung s23 gri",
        "redmi note 13 pro",
        "poco x6 pro 512 gb",
        "macbook air m2 8 gb",
        "hp victus 16 oyuncu laptop",
        "poco 512 gb",
        "32 gb ram oyuncu laptop",
        "32/32 mavi pantolon",
        "10000 40000 tl arası iphone",
        "10000 tl ile 40000 tl arası iphone",
        "40000 tl altı iphone",
        "10000 tl üstü telefon",
        "pahalı telefon",
        "en pahalı telefon",
        "ucuz telefon",
        "en ucuz laptop",
        "pahalı iphone",
        "10000 40000 tl arası en pahalı iphone",
        "pembe kulaklık",
        "1000 TL altı stokta olan kablosuz kulaklık öner",
        "teslim edilen kargoları listele",
        "hasarlı gelen ürün iadelerini göster",
        "yüksek puanlı ayakkabı yorumları",
        "iphone 11 yorumları",
        "iphone 11 için yorumlar",
        "samsung s23 yorumları",
        "macbook air m2 yorumları",
        "düşük puanlı iphone yorumları",
        "yüksek puanlı samsung yorumları",
        "kötü yorumlar",
        "en kötü yorumlar",
        "olumsuz yorumlar",
        "düşük puanlı yorumlar",
        "düşük puanlı ayakkabı yorumları",
        "1 yıldız yorumlar",
        "2 yıldızlı yorumlar",
        "3 puanlı yorumlar",
        "5 yıldız yorumlar",
        "3 puan altı yorumlar",
        "2 puan ve altı yorumlar",
        "4 puan ve üzeri yorumlar",
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
