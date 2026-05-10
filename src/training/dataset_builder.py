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


def build_product_queries(record: dict[str, Any]) -> list[str]:
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

    queries: list[str] = []

    queries.append(f"{title} öner")
    queries.append(f"{title} hakkında bilgi ver")

    if marka:
        queries.append(f"{marka} marka ürünleri göster")
        queries.append(f"{marka} {title} var mı")

    if kategoriler:
        kategori = kategoriler[0]
        queries.append(f"{kategori} kategorisindeki ürünleri göster")
        queries.append(f"{kategori} öner")

        if fiyat is not None:
            queries.append(f"{fiyat} TL civarında {kategori} öner")
            queries.append(f"{fiyat} TL altı {kategori} var mı")

        if stok is not None and int(stok) > 0:
            queries.append(f"stokta olan {kategori} öner")
            queries.append(f"stokta {kategori} var mı")

    if varyant_adi:
        queries.append(f"{varyant_adi} renk veya varyant ürünleri göster")

    return queries


def build_review_queries(record: dict[str, Any]) -> list[str]:
    """
    Ürün yorumlarından query üretir.
    """
    metadata = record["metadata"]

    urun = metadata.get("urun")
    marka = metadata.get("marka")
    puan = metadata.get("puan")
    kategoriler = metadata.get("kategoriler", [])
    ust_kategoriler = metadata.get("ust_kategoriler", [])

    queries: list[str] = []

    if urun:
        queries.append(f"{urun} yorumları")
        queries.append(f"{urun} kullanıcı yorumu")
        queries.append(f"{urun} alanlar memnun mu")

    if marka:
        queries.append(f"{marka} ürün yorumları")

    if puan is not None:
        queries.append(f"{puan} puanlı yorumları göster")

    if kategoriler:
        kategori = kategoriler[0]
        queries.append(f"{kategori} yorumları")
        queries.append(f"yüksek puanlı {kategori} yorumları")

    if ust_kategoriler:
        ust_kategori = ust_kategoriler[0]
        queries.append(f"{ust_kategori} yorumları")
        queries.append(f"en az 4 puan alan {ust_kategori} yorumları")

    return queries


def build_order_queries(record: dict[str, Any]) -> list[str]:
    """
    Sipariş kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    siparis_no = metadata.get("siparis_no")
    durum = metadata.get("durum")
    musteri = metadata.get("musteri_ad_soyad")

    queries: list[str] = []

    if siparis_no:
        queries.append(f"{siparis_no} numaralı sipariş")
        queries.append(f"{siparis_no} sipariş durumunu göster")

    if durum:
        queries.append(f"{durum} durumundaki siparişleri listele")

    if musteri:
        queries.append(f"{musteri} müşterisinin siparişleri")

    return queries


def build_cargo_queries(record: dict[str, Any]) -> list[str]:
    """
    Kargo kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    siparis_no = metadata.get("siparis_no")
    durum = metadata.get("durum")
    kargo_firmasi = metadata.get("kargo_firmasi")
    takip_no = metadata.get("takip_no")

    queries: list[str] = []

    if siparis_no:
        queries.append(f"{siparis_no} kargo durumu")
        queries.append(f"{siparis_no} kargo takibi")

    if durum:
        queries.append(f"{durum} kargoları listele")

    if kargo_firmasi:
        queries.append(f"{kargo_firmasi} kargo kayıtları")

    if takip_no:
        queries.append(f"{takip_no} takip numaralı kargo")

    return queries


def build_return_queries(record: dict[str, Any]) -> list[str]:
    """
    İade kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    siparis_no = metadata.get("siparis_no")
    durum = metadata.get("durum")
    neden = metadata.get("neden")

    queries: list[str] = []

    queries.append("iade kayıtlarını göster")
    queries.append("ürün iade taleplerini listele")

    if siparis_no:
        queries.append(f"{siparis_no} iade kaydı")

    if durum:
        queries.append(f"{durum} durumundaki iadeler")

    if neden:
        queries.append("hasarlı gelen ürün iadeleri")
        queries.append("yanlış ürün veya hasarlı ürün iade talepleri")

    return queries


def build_coupon_queries(record: dict[str, Any]) -> list[str]:
    """
    Kupon kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    kod = metadata.get("kod")
    indirim_turu = metadata.get("indirim_turu")
    aktif_mi = metadata.get("aktif_mi")

    queries: list[str] = []

    queries.append("kuponları göster")
    queries.append("indirim kampanyalarını listele")

    if kod:
        queries.append(f"{kod} kuponu")
        queries.append(f"{kod} indirim kodu geçerli mi")

    if indirim_turu:
        queries.append(f"{indirim_turu} indirimli kuponlar")

    if aktif_mi is True:
        queries.append("aktif kuponları göster")
    elif aktif_mi is False:
        queries.append("pasif kuponları göster")

    return queries


def build_customer_queries(record: dict[str, Any]) -> list[str]:
    """
    Müşteri kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    ad = metadata.get("ad")
    soyad = metadata.get("soyad")
    il = metadata.get("il")
    ilce = metadata.get("ilce")

    queries: list[str] = []

    if ad and soyad:
        queries.append(f"{ad} {soyad} müşteri bilgisi")
        queries.append(f"{ad} {soyad} adres bilgisi")

    if il:
        queries.append(f"{il} ilindeki müşteriler")

    if ilce:
        queries.append(f"{ilce} ilçesindeki müşteriler")

    return queries


def build_category_queries(record: dict[str, Any]) -> list[str]:
    """
    Kategori kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    kategori = metadata.get("kategori")
    ust_kategori = metadata.get("ust_kategori")

    queries: list[str] = []

    if kategori:
        queries.append(f"{kategori} kategorisi")
        queries.append(f"{kategori} ürünleri")

    if ust_kategori:
        queries.append(f"{ust_kategori} alt kategorileri")
        queries.append(f"{ust_kategori} kategorisine bağlı ürünler")

    return queries


def build_brand_queries(record: dict[str, Any]) -> list[str]:
    """
    Marka kayıtlarından query üretir.
    """
    metadata = record["metadata"]

    marka = metadata.get("marka")

    queries: list[str] = []

    if marka:
        queries.append(f"{marka} markası")
        queries.append(f"{marka} ürünleri")
        queries.append(f"{marka} marka ürünleri göster")

    return queries


def build_queries_for_record(record: dict[str, Any]) -> list[str]:
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
        queries = build_queries_for_record(record)

        for query in queries:
            pairs.append(
                {
                    "query": query,
                    "positive_text": record["content"],
                    "source_table": record["source_table"],
                    "source_id": record["source_id"],
                    "title": record["title"],
                }
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
