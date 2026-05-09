from typing import Any

from psycopg.types.json import Jsonb
from tqdm import tqdm

from src.database.db import get_db_connection
from src.embedding.model_loader import encode_texts, load_embedding_model


SEMANTIC_SOURCE_VIEW = "vw_semantic_all"
SEMANTIC_INDEX_TABLE = "semantic_index"


def fetch_product_descriptions() -> dict[str, str]:
    """
    Ürün varyantı kayıtları için temiz ürün açıklamalarını okur.

    vw_semantic_urunler embedding metninde açıklamayı kullanır; bu fonksiyon
    aynı açıklamayı UI tarafında temiz gösterebilmek için metadata'ya eklemek
    üzere varyant_id -> aciklama eşlemesi döndürür.
    """
    query = """
        SELECT
            uv.varyant_id,
            u.aciklama
        FROM public.urun_varyantlari uv
        JOIN public.urunler u
            ON u.urun_id = uv.urun_id
        WHERE u.aciklama IS NOT NULL
          AND btrim(u.aciklama) <> '';
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    return {str(row[0]): row[1] for row in rows}


def enrich_product_variant_metadata(records: list[dict[str, Any]]) -> None:
    """
    urun_varyantlari semantic kayıtlarının metadata alanına temiz açıklama ekler.
    """
    product_descriptions = fetch_product_descriptions()

    for record in records:
        if record["kaynak_tablo"] != "urun_varyantlari":
            continue

        description = product_descriptions.get(str(record["kaynak_id"]))
        if not description:
            continue

        metadata = dict(record["metadata"] or {})
        metadata["aciklama"] = description
        record["metadata"] = metadata


def fetch_semantic_records() -> list[dict[str, Any]]:
    """
    vw_semantic_all view'ından embedding üretilecek kayıtları okur.

    Dönen her kayıt:
        kaynak_tablo
        kaynak_id
        baslik
        icerik
        metadata
    alanlarını içerir.
    """
    query = f"""
        SELECT
            kaynak_tablo,
            kaynak_id,
            baslik,
            icerik,
            metadata
        FROM public.{SEMANTIC_SOURCE_VIEW}
        ORDER BY kaynak_tablo, baslik;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    records: list[dict[str, Any]] = []

    for row in rows:
        records.append(
            {
                "kaynak_tablo": row[0],
                "kaynak_id": row[1],
                "baslik": row[2],
                "icerik": row[3],
                "metadata": row[4],
            }
        )

    enrich_product_variant_metadata(records)

    return records


def clear_semantic_index() -> None:
    """
    semantic_index tablosunu temizler.

    Yeniden index oluşturmak istediğimizde kullanılabilir.
    """
    query = f"TRUNCATE TABLE public.{SEMANTIC_INDEX_TABLE};"

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)


def upsert_semantic_records(records: list[dict[str, Any]], embeddings) -> None:
    """
    Üretilen embedding vektörlerini semantic_index tablosuna yazar.

    Aynı kaynak_tablo + kaynak_id varsa günceller.
    Yoksa yeni kayıt ekler.
    """
    query = f"""
        INSERT INTO public.{SEMANTIC_INDEX_TABLE}
        (
            kaynak_tablo,
            kaynak_id,
            baslik,
            icerik,
            metadata,
            embedding,
            guncelleme_tarihi
        )
        VALUES
        (
            %(kaynak_tablo)s,
            %(kaynak_id)s,
            %(baslik)s,
            %(icerik)s,
            %(metadata)s,
            %(embedding)s,
            now()
        )
        ON CONFLICT (kaynak_tablo, kaynak_id)
        DO UPDATE SET
            baslik = EXCLUDED.baslik,
            icerik = EXCLUDED.icerik,
            metadata = EXCLUDED.metadata,
            embedding = EXCLUDED.embedding,
            guncelleme_tarihi = now();
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for record, embedding in tqdm(
                zip(records, embeddings),
                total=len(records),
                desc="semantic_index yazılıyor",
            ):
                params = {
                    "kaynak_tablo": record["kaynak_tablo"],
                    "kaynak_id": record["kaynak_id"],
                    "baslik": record["baslik"],
                    "icerik": record["icerik"],
                    "metadata": Jsonb(record["metadata"]),
                    "embedding": embedding.tolist(),
                }

                cur.execute(query, params)


def build_semantic_index(clear_before_insert: bool = False) -> None:
    """
    Ana semantic index oluşturma akışı.

    1. vw_semantic_all view'ından kayıtları okur.
    2. SentenceTransformer modeliyle embedding üretir.
    3. semantic_index tablosuna yazar.
    """
    records = fetch_semantic_records()

    if not records:
        print("Embedding üretilecek kayıt bulunamadı.")
        return

    print(f"Toplam semantic kayıt: {len(records)}")

    if clear_before_insert:
        print("semantic_index tablosu temizleniyor...")
        clear_semantic_index()

    texts = [record["icerik"] for record in records]

    print("Embedding modeli yükleniyor...")
    model = load_embedding_model()

    print("Embedding üretiliyor...")
    embeddings = encode_texts(model, texts)

    print("semantic_index tablosuna yazılıyor...")
    upsert_semantic_records(records, embeddings)

    print("semantic_index oluşturma işlemi tamamlandı.")


def count_semantic_index_records() -> int:
    """
    semantic_index tablosundaki kayıt sayısını döndürür.
    """
    query = f"SELECT COUNT(*) FROM public.{SEMANTIC_INDEX_TABLE};"

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            count = cur.fetchone()[0]

    return count


if __name__ == "__main__":
    build_semantic_index(clear_before_insert=False)
    total = count_semantic_index_records()
    print(f"semantic_index kayıt sayısı: {total}")
