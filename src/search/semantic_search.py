from typing import Any

from pgvector.psycopg import Vector

from src.config_loader import load_yaml_config
from src.database.db import get_db_connection
from src.embedding.model_loader import encode_text, load_embedding_model


def get_search_config() -> dict[str, Any]:
    """
    config/search.yaml dosyasındaki arama ayarlarını okur.
    """
    config = load_yaml_config("config/search.yaml")
    return config["search"]


def semantic_search(query_text: str, limit: int | None = None) -> list[dict[str, Any]]:
    """
    Kullanıcı sorgusunu embedding'e çevirir ve semantic_index tablosunda
    en benzer kayıtları getirir.

    Args:
        query_text: Kullanıcının doğal dil sorgusu.
        limit: Kaç sonuç döneceği. None ise config/search.yaml içindeki default_limit kullanılır.

    Returns:
        Benzerlik sırasına göre sonuç listesi.
    """
    search_config = get_search_config()

    if limit is None:
        limit = search_config.get("default_limit", 5)

    max_limit = search_config.get("max_limit", 20)
    limit = min(limit, max_limit)

    print("Embedding modeli yükleniyor...")
    model = load_embedding_model()

    print("Sorgu embedding'e çevriliyor...")
    query_embedding = encode_text(model, query_text)

    sql = """
        SELECT
            kaynak_tablo,
            kaynak_id,
            baslik,
            icerik,
            metadata,
            embedding <=> %(query_embedding)s AS distance
        FROM public.semantic_index
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %(query_embedding)s
        LIMIT %(limit)s;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                {
                    "query_embedding": Vector(query_embedding.tolist()),
                    "limit": limit,
                },
            )

            rows = cur.fetchall()

    results: list[dict[str, Any]] = []

    for row in rows:
        distance = float(row[5])

        # Cosine distance küçükse daha benzerdir.
        # Basit okunabilirlik için similarity_score = 1 - distance yapıyoruz.
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
    Terminalden hızlı semantic search testi yapar.
    """
    test_queries = [
        "1000 TL altı kablosuz kulaklık öner",
        "hasarlı gelen ürün iadelerini göster",
        "teslim edilen kargoları listele",
        "oyuncu mouse öner",
        "yüksek puanlı ayakkabı yorumları",
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