from typing import Any

from src.search.query_parser import ParsedQuery


def format_price(value: Any, currency: str | None = "TRY") -> str:
    """
    Fiyat bilgisini okunabilir hale getirir.
    """
    if value is None:
        return "Belirtilmemiş"

    try:
        return f"{float(value):,.2f} {currency}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return f"{value} {currency or ''}".strip()


def get_metadata(result: dict[str, Any]) -> dict[str, Any]:
    """
    Arama sonucundaki metadata alanını güvenli şekilde döndürür.
    """
    metadata = result.get("metadata")

    if isinstance(metadata, dict):
        return metadata

    return {}


def generate_product_answer(
    query: str,
    results: list[dict[str, Any]],
    parsed_query: ParsedQuery,
) -> str:
    """
    Ürün/varyant sonuçları için kullanıcıya doğal cevap üretir.
    """
    if not results:
        return "Sorgunuza uygun ürün bulunamadı."

    best = results[0]
    metadata = get_metadata(best)

    title = best.get("baslik", "Ürün")
    brand = metadata.get("marka", "Belirtilmemiş")
    price = metadata.get("satis_fiyati")
    currency = metadata.get("para_birimi", "TRY")
    stock = metadata.get("stok")
    score = best.get("similarity_score", 0)

    parts = []

    parts.append(f"Sorgunuza en uygun ürün **{title}** görünüyor.")
    parts.append(f"Marka: **{brand}**.")
    parts.append(f"Satış fiyatı: **{format_price(price, currency)}**.")

    if stock is not None:
        parts.append(f"Stok adedi: **{stock}**.")

    if parsed_query.max_price is not None:
        parts.append(f"Bu ürün, belirttiğiniz **{parsed_query.max_price:.0f} TL altı** filtresine uygundur.")

    if parsed_query.in_stock_only:
        parts.append("Ayrıca ürün stokta bulunduğu için stok filtresini de karşılıyor.")

    parts.append(f"Benzerlik skoru: **{score:.4f}**.")

    if len(results) > 1:
        parts.append("\nAlternatif sonuçlar:")
        for index, result in enumerate(results[1:], start=2):
            alt_meta = get_metadata(result)
            alt_price = alt_meta.get("satis_fiyati")
            alt_currency = alt_meta.get("para_birimi", "TRY")
            alt_stock = alt_meta.get("stok")
            parts.append(
                f"{index}. {result.get('baslik')} — "
                f"{format_price(alt_price, alt_currency)}, stok: {alt_stock}"
            )

    return "\n".join(parts)


def generate_review_answer(
    query: str,
    results: list[dict[str, Any]],
    parsed_query: ParsedQuery,
) -> str:
    """
    Ürün yorumları için doğal cevap üretir.
    """
    if not results:
        return "Sorgunuza uygun ürün yorumu bulunamadı."

    parts = ["Sorgunuza uygun ürün yorumları şunlar:"]

    for index, result in enumerate(results, start=1):
        metadata = get_metadata(result)

        title = result.get("baslik", "Yorum")
        rating = metadata.get("puan", "Belirtilmemiş")
        brand = metadata.get("marka", "Belirtilmemiş")
        score = result.get("similarity_score", 0)

        parts.append(
            f"{index}. **{title}**\n"
            f"   Marka: {brand} | Puan: {rating} | Benzerlik: {score:.4f}"
        )

    return "\n".join(parts)


def generate_cargo_answer(
    query: str,
    results: list[dict[str, Any]],
    parsed_query: ParsedQuery,
) -> str:
    """
    Kargo kayıtları için doğal cevap üretir.
    """
    if not results:
        return "Sorgunuza uygun kargo kaydı bulunamadı."

    parts = ["Sorgunuza uygun kargo kayıtları:"]

    for index, result in enumerate(results, start=1):
        metadata = get_metadata(result)

        order_no = metadata.get("siparis_no", "Belirtilmemiş")
        cargo_company = metadata.get("kargo_firmasi", "Belirtilmemiş")
        tracking_no = metadata.get("takip_no", "Belirtilmemiş")
        status = metadata.get("durum", "Belirtilmemiş")
        customer = metadata.get("musteri_ad_soyad", "Belirtilmemiş")
        score = result.get("similarity_score", 0)

        parts.append(
            f"{index}. **{order_no}**\n"
            f"   Firma: {cargo_company} | Takip No: {tracking_no}\n"
            f"   Durum: {status} | Müşteri: {customer} | Benzerlik: {score:.4f}"
        )

    return "\n".join(parts)


def generate_return_answer(
    query: str,
    results: list[dict[str, Any]],
    parsed_query: ParsedQuery,
) -> str:
    """
    İade kayıtları için doğal cevap üretir.
    """
    if not results:
        return "Sorgunuza uygun iade kaydı bulunamadı."

    parts = ["Sorgunuza uygun iade kayıtları:"]

    for index, result in enumerate(results, start=1):
        metadata = get_metadata(result)

        order_no = metadata.get("siparis_no", "Belirtilmemiş")
        status = metadata.get("durum", "Belirtilmemiş")
        reason = metadata.get("neden", "Belirtilmemiş")
        customer = metadata.get("musteri_ad_soyad", "Belirtilmemiş")
        score = result.get("similarity_score", 0)

        parts.append(
            f"{index}. **{order_no}**\n"
            f"   Müşteri: {customer}\n"
            f"   Durum: {status}\n"
            f"   Neden: {reason}\n"
            f"   Benzerlik: {score:.4f}"
        )

    return "\n".join(parts)


def generate_coupon_answer(
    query: str,
    results: list[dict[str, Any]],
    parsed_query: ParsedQuery,
) -> str:
    """
    Kupon kayıtları için doğal cevap üretir.
    """
    if not results:
        return "Sorgunuza uygun kupon bulunamadı."

    parts = ["Sorgunuza uygun kuponlar:"]

    for index, result in enumerate(results, start=1):
        metadata = get_metadata(result)

        code = metadata.get("kod", "Belirtilmemiş")
        discount_type = metadata.get("indirim_turu", "Belirtilmemiş")
        value = metadata.get("deger", "Belirtilmemiş")
        active = metadata.get("aktif_mi")
        score = result.get("similarity_score", 0)

        active_text = "Aktif" if active else "Pasif"

        parts.append(
            f"{index}. **{code}**\n"
            f"   İndirim türü: {discount_type} | Değer: {value}\n"
            f"   Durum: {active_text} | Benzerlik: {score:.4f}"
        )

    return "\n".join(parts)


def generate_order_answer(
    query: str,
    results: list[dict[str, Any]],
    parsed_query: ParsedQuery,
) -> str:
    """
    Sipariş kayıtları için doğal cevap üretir.
    """
    if not results:
        return "Sorgunuza uygun sipariş bulunamadı."

    parts = ["Sorgunuza uygun sipariş kayıtları:"]

    for index, result in enumerate(results, start=1):
        metadata = get_metadata(result)

        order_no = metadata.get("siparis_no", "Belirtilmemiş")
        customer = metadata.get("musteri_ad_soyad", "Belirtilmemiş")
        status = metadata.get("durum", "Belirtilmemiş")
        total = metadata.get("genel_toplam_tutar")
        currency = metadata.get("para_birimi", "TRY")
        score = result.get("similarity_score", 0)

        parts.append(
            f"{index}. **{order_no}**\n"
            f"   Müşteri: {customer} | Durum: {status}\n"
            f"   Genel toplam: {format_price(total, currency)} | Benzerlik: {score:.4f}"
        )

    return "\n".join(parts)


def generate_generic_answer(
    query: str,
    results: list[dict[str, Any]],
    parsed_query: ParsedQuery,
) -> str:
    """
    Genel sonuçlar için fallback cevap üretir.
    """
    if not results:
        return "Sorgunuza uygun sonuç bulunamadı."

    parts = ["Sorgunuza en yakın sonuçlar:"]

    for index, result in enumerate(results, start=1):
        score = result.get("similarity_score", 0)

        parts.append(
            f"{index}. **{result.get('baslik')}**\n"
            f"   Kaynak tablo: {result.get('kaynak_tablo')} | Benzerlik: {score:.4f}"
        )

    return "\n".join(parts)


def generate_answer(
    query: str,
    results: list[dict[str, Any]],
    parsed_query: ParsedQuery,
) -> str:
    """
    ParsedQuery intent bilgisine göre uygun cevap üreticisini seçer.
    """
    if parsed_query.intent == "product":
        return generate_product_answer(query, results, parsed_query)

    if parsed_query.intent == "review":
        return generate_review_answer(query, results, parsed_query)

    if parsed_query.intent == "cargo":
        return generate_cargo_answer(query, results, parsed_query)

    if parsed_query.intent == "return":
        return generate_return_answer(query, results, parsed_query)

    if parsed_query.intent == "coupon":
        return generate_coupon_answer(query, results, parsed_query)

    if parsed_query.intent == "order":
        return generate_order_answer(query, results, parsed_query)

    return generate_generic_answer(query, results, parsed_query)