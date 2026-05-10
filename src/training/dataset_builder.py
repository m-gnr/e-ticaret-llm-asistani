import json
from pathlib import Path
from typing import Any

from src.config_loader import get_project_root, load_yaml_config
from src.database.db import get_db_connection


def get_training_config() -> dict[str, Any]:
    config = load_yaml_config("config/model.yaml")
    return config["training"]


def get_output_path() -> str:
    training_config = get_training_config()
    return training_config["full_dataset_path"]


def fetch_semantic_records() -> list[dict[str, Any]]:
    """
    Fine-tuning veri seti üretmek için semantic kayıtları okur.

    Burada doğrudan semantic_index yerine vw_semantic_all kullanıyoruz.
    Çünkü eğitim verisi üretirken embedding'e değil, metinsel içeriğe ihtiyacımız var.
    """
    query = """
        SELECT
            kaynak_tablo,
            kaynak_id,
            baslik,
            icerik,
            metadata
        FROM public.vw_semantic_all
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
                "source_table": row[0],
                "source_id": str(row[1]),
                "title": row[2],
                "content": row[3],
                "metadata": row[4],
            }
        )

    return records


def build_expected_exact(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_table": record["source_table"],
        "source_id": record["source_id"],
        "title": record["title"],
    }


def make_query_spec(
    query: str,
    query_type: str,
    evaluation_mode: str,
) -> dict[str, str]:
    return {
        "query": query,
        "query_type": query_type,
        "evaluation_mode": evaluation_mode,
    }


def make_pair(
    query: str,
    record: dict[str, Any],
    query_type: str,
    evaluation_mode: str = "exact_id",
) -> dict[str, Any]:
    return {
        "query": query,
        "positive_text": record["content"],
        "source_table": record["source_table"],
        "source_id": record["source_id"],
        "title": record["title"],
        "query_type": query_type,
        "evaluation_mode": evaluation_mode,
        "expected": build_expected_exact(record),
    }


def build_product_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Ürün/varyant kayıtlarından kullanıcı sorgusuna benzeyen query'ler üretir.
    """
    metadata = record["metadata"]
    title = record["title"]

    marka = metadata.get("marka")
    fiyat = metadata.get("satis_fiyati")
    stok = metadata.get("stok")
    kategoriler = metadata.get("kategoriler", [])
    varyant_adi = metadata.get("varyant_adi")

    queries: list[dict[str, str]] = []

    queries.append(make_query_spec(f"{title} öner", "specific", "exact_id"))
    queries.append(make_query_spec(f"{title} hakkında bilgi ver", "specific", "exact_id"))

    if marka:
        queries.append(make_query_spec(f"{marka} marka ürünleri göster", "generic", "skip"))
        queries.append(make_query_spec(f"{marka} {title} var mı", "specific", "exact_id"))

    if kategoriler:
        kategori = kategoriler[0]
        queries.append(make_query_spec(f"{kategori} kategorisindeki ürünleri göster", "generic", "skip"))
        queries.append(make_query_spec(f"{kategori} öner", "generic", "skip"))

        if fiyat is not None:
            queries.append(make_query_spec(f"{fiyat} TL civarında {kategori} öner", "attribute", "metadata"))
            queries.append(make_query_spec(f"{fiyat} TL altı {kategori} var mı", "attribute", "metadata"))

        if stok is not None and int(stok) > 0:
            queries.append(make_query_spec(f"stokta olan {kategori} öner", "attribute", "metadata"))
            queries.append(make_query_spec(f"stokta {kategori} var mı", "attribute", "metadata"))

    if varyant_adi:
        queries.append(make_query_spec(f"{varyant_adi} renk veya varyant ürünleri göster", "attribute", "metadata"))

    return queries


def build_review_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Ürün yorumlarından query üretir.
    """
    metadata = record["metadata"]

    urun = metadata.get("urun")
    marka = metadata.get("marka")
    puan = metadata.get("puan")
    kategoriler = metadata.get("kategoriler", [])
    ust_kategoriler = metadata.get("ust_kategoriler", [])

    title = record["title"]

    queries: list[dict[str, str]] = []

    if title:
        queries.append(make_query_spec(f"{title} yorumunu göster", "attribute", "metadata"))

    if urun:
        queries.append(make_query_spec(f"{urun} yorumları", "attribute", "metadata"))
        queries.append(make_query_spec(f"{urun} kullanıcı yorumu", "attribute", "metadata"))
        queries.append(make_query_spec(f"{urun} alanlar memnun mu", "attribute", "metadata"))

    if marka:
        queries.append(make_query_spec(f"{marka} ürün yorumları", "attribute", "metadata"))

    if puan is not None:
        queries.append(make_query_spec(f"{puan} puanlı yorumları göster", "attribute", "metadata"))

    if kategoriler:
        kategori = kategoriler[0]
        queries.append(make_query_spec(f"{kategori} yorumları", "attribute", "metadata"))
        queries.append(make_query_spec(f"yüksek puanlı {kategori} yorumları", "attribute", "metadata"))

    if ust_kategoriler:
        ust_kategori = ust_kategoriler[0]
        queries.append(make_query_spec(f"{ust_kategori} yorumları", "attribute", "metadata"))
        queries.append(make_query_spec(f"en az 4 puan alan {ust_kategori} yorumları", "attribute", "metadata"))

    return queries


def build_order_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Sipariş kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    siparis_no = metadata.get("siparis_no")
    durum = metadata.get("durum")
    musteri = metadata.get("musteri_ad_soyad")

    queries: list[dict[str, str]] = []

    if siparis_no:
        queries.append(make_query_spec(f"{siparis_no} numaralı sipariş", "navigational", "exact_id"))
        queries.append(make_query_spec(f"{siparis_no} sipariş durumunu göster", "navigational", "exact_id"))

    if durum:
        queries.append(make_query_spec(f"{durum} durumundaki siparişleri listele", "generic", "skip"))

    if musteri:
        queries.append(make_query_spec(f"{musteri} müşterisinin siparişleri", "generic", "skip"))

    return queries


def build_cargo_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Kargo kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    siparis_no = metadata.get("siparis_no")
    durum = metadata.get("durum")
    kargo_firmasi = metadata.get("kargo_firmasi")
    takip_no = metadata.get("takip_no")

    queries: list[dict[str, str]] = []

    if siparis_no:
        queries.append(make_query_spec(f"{siparis_no} kargo durumu", "navigational", "exact_id"))
        queries.append(make_query_spec(f"{siparis_no} kargo takibi", "navigational", "exact_id"))

    if durum:
        queries.append(make_query_spec(f"{durum} kargoları listele", "generic", "skip"))

    if kargo_firmasi:
        queries.append(make_query_spec(f"{kargo_firmasi} kargo kayıtları", "generic", "skip"))

    if takip_no:
        queries.append(make_query_spec(f"{takip_no} takip numaralı kargo", "navigational", "exact_id"))

    return queries


def build_return_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    İade kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    siparis_no = metadata.get("siparis_no")
    durum = metadata.get("durum")
    neden = metadata.get("neden")

    queries: list[dict[str, str]] = []

    queries.append(make_query_spec("iade kayıtlarını göster", "generic", "skip"))
    queries.append(make_query_spec("ürün iade taleplerini listele", "generic", "skip"))

    if siparis_no:
        queries.append(make_query_spec(f"{siparis_no} iade kaydı", "navigational", "exact_id"))

    if durum:
        queries.append(make_query_spec(f"{durum} durumundaki iadeler", "generic", "skip"))

    if neden:
        queries.append(make_query_spec("hasarlı gelen ürün iadeleri", "generic", "skip"))
        queries.append(make_query_spec("yanlış ürün veya hasarlı ürün iade talepleri", "generic", "skip"))

    return queries


def build_coupon_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Kupon kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    kod = metadata.get("kod")
    indirim_turu = metadata.get("indirim_turu")
    aktif_mi = metadata.get("aktif_mi")

    queries: list[dict[str, str]] = []

    queries.append(make_query_spec("kuponları göster", "generic", "skip"))
    queries.append(make_query_spec("indirim kampanyalarını listele", "generic", "skip"))

    if kod:
        queries.append(make_query_spec(f"{kod} kuponu", "navigational", "exact_id"))
        queries.append(make_query_spec(f"{kod} indirim kodu geçerli mi", "navigational", "exact_id"))

    if indirim_turu:
        queries.append(make_query_spec(f"{indirim_turu} indirimli kuponlar", "generic", "skip"))

    if aktif_mi is True:
        queries.append(make_query_spec("aktif kuponları göster", "attribute", "metadata"))
    elif aktif_mi is False:
        queries.append(make_query_spec("pasif kuponları göster", "attribute", "metadata"))

    return queries


def build_customer_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Müşteri kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    ad = metadata.get("ad")
    soyad = metadata.get("soyad")
    il = metadata.get("il")
    ilce = metadata.get("ilce")

    queries: list[dict[str, str]] = []

    if ad and soyad:
        queries.append(make_query_spec(f"{ad} {soyad} müşteri bilgisi", "navigational", "exact_id"))
        queries.append(make_query_spec(f"{ad} {soyad} adres bilgisi", "navigational", "exact_id"))

    if il:
        queries.append(make_query_spec(f"{il} ilindeki müşteriler", "generic", "skip"))

    if ilce:
        queries.append(make_query_spec(f"{ilce} ilçesindeki müşteriler", "generic", "skip"))

    return queries


def build_category_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Kategori kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    kategori = metadata.get("kategori")
    ust_kategori = metadata.get("ust_kategori")

    queries: list[dict[str, str]] = []

    if kategori:
        queries.append(make_query_spec(f"{kategori} kategorisi", "generic", "skip"))
        queries.append(make_query_spec(f"{kategori} ürünleri", "generic", "skip"))

    if ust_kategori:
        queries.append(make_query_spec(f"{ust_kategori} alt kategorileri", "generic", "skip"))
        queries.append(make_query_spec(f"{ust_kategori} kategorisine bağlı ürünler", "generic", "skip"))

    return queries


def build_brand_queries(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Marka kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    marka = metadata.get("marka")

    queries: list[dict[str, str]] = []

    if marka:
        queries.append(make_query_spec(f"{marka} markası", "generic", "skip"))
        queries.append(make_query_spec(f"{marka} ürünleri", "generic", "skip"))
        queries.append(make_query_spec(f"{marka} marka ürünleri göster", "generic", "skip"))

    return queries


def build_queries_for_record(record: dict[str, Any]) -> list[dict[str, str]]:
    """
    Kaynak tabloya göre uygun query üreticisini seçer.
    """
    source_table = record["source_table"]

    if source_table == "urun_varyantlari":
        return build_product_queries(record)

    if source_table == "urun_yorumlari":
        return build_review_queries(record)

    if source_table == "siparisler":
        return build_order_queries(record)

    if source_table == "kargolar":
        return build_cargo_queries(record)

    if source_table == "iadeler":
        return build_return_queries(record)

    if source_table == "kuponlar":
        return build_coupon_queries(record)

    if source_table == "musteriler":
        return build_customer_queries(record)

    if source_table == "kategoriler":
        return build_category_queries(record)

    if source_table == "markalar":
        return build_brand_queries(record)

    return []


def build_training_pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Semantic kayıtlardan query-positive_text çiftleri üretir.
    """
    pairs: list[dict[str, Any]] = []

    for record in records:
        query_specs = build_queries_for_record(record)

        for query_spec in query_specs:
            pairs.append(
                make_pair(
                    query=query_spec["query"],
                    record=record,
                    query_type=query_spec["query_type"],
                    evaluation_mode=query_spec["evaluation_mode"],
                )
            )

    return pairs


def save_jsonl(records: list[dict[str, Any]], output_path: str) -> Path:
    """
    Eğitim çiftlerini JSONL dosyasına kaydeder.
    """
    project_root = get_project_root()
    full_path = project_root / output_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    with full_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    return full_path


def run() -> None:
    records = fetch_semantic_records()
    print(f"Semantic kayıt sayısı: {len(records)}")

    pairs = build_training_pairs(records)
    print(f"Üretilen training pair sayısı: {len(pairs)}")

    output_file = save_jsonl(pairs, get_output_path())
    print(f"Training dataset kaydedildi: {output_file}")

    print("\nİlk 5 örnek:")
    for pair in pairs[:5]:
        print("-" * 80)
        print(json.dumps(pair, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
