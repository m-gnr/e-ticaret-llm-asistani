import re
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ParsedQuery:
    original_query: str
    search_text: str
    intent: str | None
    source_tables: list[str]
    max_price: float | None = None
    min_price: float | None = None
    in_stock_only: bool = False
    out_of_stock_only: bool = False
    min_rating: int | None = None
    category: str | None = None
    brand: str | None = None
    status: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


INTENT_TABLES = {
    "product": ["urun_varyantlari"],
    "review": ["urun_yorumlari"],
    "return": ["iadeler"],
    "cargo": ["kargolar"],
    "order": ["siparisler"],
    "coupon": ["kuponlar"],
    "customer": ["musteriler"],
}


INTENT_KEYWORDS = {
    "return": [
        "iade",
        "iadeler",
        "hasarlı",
        "kusurlu",
        "geri gönder",
        "geri gonder",
    ],
    "cargo": [
        "kargo",
        "kargolar",
        "teslimat",
        "takip",
        "teslim edilen",
        "yolda",
    ],
    "review": [
        "yorum",
        "yorumlar",
        "puan",
        "değerlendirme",
        "degerlendirme",
        "memnuniyet",
        "şikayet",
        "sikayet",
    ],
    "order": [
        "sipariş",
        "siparis",
        "siparişler",
        "siparisler",
        "sipariş no",
        "siparis no",
    ],
    "coupon": [
        "kupon",
        "indirim",
        "kampanya",
    ],
    "customer": [
        "müşteri",
        "musteri",
        "kullanıcı",
        "kullanici",
        "adres",
    ],
    "product": [
        "ürün",
        "urun",
        "öner",
        "oner",
        "tavsiye",
        "satın al",
        "satin al",
        "kulaklık",
        "kulaklik",
        "mouse",
        "klavye",
        "laptop",
        "telefon",
        "ayakkabı",
        "ayakkabi",
        "tişört",
        "tisort",
    ],
}


CATEGORY_KEYWORDS = {
    # Daha spesifik kategoriler önce gelmeli
    "Oyuncu Mouse": ["oyuncu mouse", "gaming mouse"],
    "Oyuncu Klavyesi": ["oyuncu klavyesi", "gaming klavye", "rgb klavye"],
    "Oyuncu Kulaklığı": [
        "oyuncu kulaklığı",
        "oyuncu kulakligi",
        "gaming kulaklık",
        "gaming kulaklik",
    ],

    "Koşu Ayakkabısı": ["koşu ayakkabısı", "kosu ayakkabisi"],
    "Spor Ayakkabı": ["spor ayakkabı", "spor ayakkabi"],
    "Günlük Ayakkabı": ["günlük ayakkabı", "gunluk ayakkabi", "sneaker"],
    "Bot": ["bot", "outdoor bot"],

    # Genel kategoriler
    "Kulaklık": [
        "kulaklık",
        "kulaklik",
        "bluetooth kulaklık",
        "kablosuz kulaklık",
    ],
    "Mouse": ["mouse", "fare", "kablosuz mouse"],
    "Klavye": ["klavye", "keyboard", "kablosuz klavye"],
    "Laptop": ["laptop", "dizüstü", "dizustu", "notebook"],
    "Telefon": ["telefon", "akıllı telefon", "akilli telefon"],
    "Şarj Cihazı": [
        "şarj cihazı",
        "sarj cihazi",
        "adaptör",
        "adapter",
        "hızlı şarj",
        "hizli sarj",
    ],
    "Powerbank": ["powerbank", "taşınabilir şarj", "tasinabilir sarj"],
    "Akıllı Saat": ["akıllı saat", "akilli saat", "watch"],
    "Kahve Makinesi": ["kahve makinesi", "türk kahvesi", "turk kahvesi"],
    "Süpürge": ["süpürge", "supurge"],
    "Tişört": ["tişört", "tisort", "t-shirt"],
    "Pantolon": ["pantolon", "jean"],
    "Sweatshirt": ["sweatshirt", "kapüşonlu", "kapusonlu"],
    "Mont": ["mont", "kışlık mont", "kislik mont"],
    "Ayakkabı": ["ayakkabı", "ayakkabi", "ayakkabılar", "ayakkabilar"],
}


BRAND_KEYWORDS = [
    "sony",
    "samsung",
    "apple",
    "xiaomi",
    "logitech",
    "philips",
    "arzum",
    "monster",
    "lenovo",
    "asus",
    "msi",
    "hp",
    "dell",
    "jbl",
    "anker",
    "huawei",
    "kingston",
    "corsair",
    "razer",
    "dyson",
    "nike",
    "adidas",
    "puma",
    "lc waikiki",
    "mavi",
    "defacto",
]


STATUS_KEYWORDS = {
    "teslim_edildi": ["teslim edildi", "teslim edilen", "teslim edilmiş"],
    "yolda": ["yolda", "kargo yolda", "dağıtımda", "dagitimda"],
    "hazirlaniyor": ["hazırlanıyor", "hazirlaniyor", "hazırlıkta"],
    "kargoya_verildi": ["kargoya verildi", "kargoda"],
    "iptal_edildi": ["iptal", "iptal edildi"],
    "iade_edildi": ["iade edildi", "iade olan"],
    "basarili": ["başarılı ödeme", "basarili odeme", "ödendi"],
    "basarisiz": ["başarısız ödeme", "basarisiz odeme"],
    "beklemede": ["beklemede", "ödeme beklemede"],
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def extract_max_price(text: str) -> float | None:
    patterns = [
        r"(\d+(?:[.,]\d+)?)\s*tl\s*altı",
        r"(\d+(?:[.,]\d+)?)\s*tl\s*altında",
        r"(\d+(?:[.,]\d+)?)\s*tl\s*aşağısı",
        r"(\d+(?:[.,]\d+)?)\s*tl\s*ye\s*kadar",
        r"(\d+(?:[.,]\d+)?)\s*tl\s*'ye\s*kadar",
        r"en fazla\s*(\d+(?:[.,]\d+)?)\s*tl",
        r"maksimum\s*(\d+(?:[.,]\d+)?)\s*tl",
        r"max\s*(\d+(?:[.,]\d+)?)\s*tl",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1).replace(",", "."))

    return None


def extract_min_price(text: str) -> float | None:
    patterns = [
        r"(\d+(?:[.,]\d+)?)\s*tl\s*üstü",
        r"(\d+(?:[.,]\d+)?)\s*tl\s*üzeri",
        r"en az\s*(\d+(?:[.,]\d+)?)\s*tl",
        r"minimum\s*(\d+(?:[.,]\d+)?)\s*tl",
        r"min\s*(\d+(?:[.,]\d+)?)\s*tl",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1).replace(",", "."))

    return None


def extract_stock_filter(text: str) -> tuple[bool, bool]:
    out_of_stock_keywords = [
        "stokta olmayan",
        "stok dışı",
        "stok disi",
        "tükenen",
        "tukenen",
        "bitmiş",
        "bitmis",
    ]

    in_stock_keywords = [
        "stokta",
        "stokta olan",
        "mevcut",
        "elde olan",
        "hazır",
        "hazir",
        "satışta",
        "satista",
    ]

    out_of_stock = any(keyword in text for keyword in out_of_stock_keywords)
    in_stock = any(keyword in text for keyword in in_stock_keywords) and not out_of_stock

    return in_stock, out_of_stock


def extract_min_rating(text: str) -> int | None:
    patterns = [
        r"en az\s*(\d)\s*puan",
        r"(\d)\s*puan\s*üstü",
        r"(\d)\s*puan\s*üzeri",
        r"minimum\s*(\d)\s*puan",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    high_rating_keywords = [
        "yüksek puanlı",
        "yuksek puanli",
        "iyi yorumlu",
        "olumlu yorumlu",
        "çok beğenilen",
        "cok begenilen",
        "en beğenilen",
        "en begenilen",
    ]

    if any(keyword in text for keyword in high_rating_keywords):
        return 4

    return None


def detect_intent(text: str) -> str | None:
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return intent

    return None


def detect_category(text: str) -> str | None:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category

    return None


def detect_brand(text: str) -> str | None:
    for brand in BRAND_KEYWORDS:
        if brand in text:
            return brand

    return None


def detect_status(text: str) -> str | None:
    for status, keywords in STATUS_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return status

    return None


def clean_search_text(text: str) -> str:
    cleaned = text

    remove_patterns = [
        r"\d+(?:[.,]\d+)?\s*tl\s*altı",
        r"\d+(?:[.,]\d+)?\s*tl\s*altında",
        r"\d+(?:[.,]\d+)?\s*tl\s*aşağısı",
        r"\d+(?:[.,]\d+)?\s*tl\s*ye\s*kadar",
        r"en fazla\s*\d+(?:[.,]\d+)?\s*tl",
        r"maksimum\s*\d+(?:[.,]\d+)?\s*tl",
        r"stokta olan",
        r"stokta",
        r"mevcut",
        r"öner",
        r"oner",
        r"tavsiye",
        r"listele",
        r"göster",
        r"goster",
    ]

    for pattern in remove_patterns:
        cleaned = re.sub(pattern, " ", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def parse_query(query: str) -> ParsedQuery:
    normalized = normalize_text(query)

    intent = detect_intent(normalized)
    source_tables = INTENT_TABLES.get(intent, [])

    max_price = extract_max_price(normalized)
    min_price = extract_min_price(normalized)
    in_stock_only, out_of_stock_only = extract_stock_filter(normalized)
    min_rating = extract_min_rating(normalized)
    category = detect_category(normalized)
    brand = detect_brand(normalized)
    status = detect_status(normalized)
    search_text = clean_search_text(normalized)

    return ParsedQuery(
        original_query=query,
        search_text=search_text,
        intent=intent,
        source_tables=source_tables,
        max_price=max_price,
        min_price=min_price,
        in_stock_only=in_stock_only,
        out_of_stock_only=out_of_stock_only,
        min_rating=min_rating,
        category=category,
        brand=brand,
        status=status,
    )


def run_demo() -> None:
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
        parsed = parse_query(query)
        print("=" * 80)
        print(f"Sorgu: {query}")
        print(parsed.to_dict())


if __name__ == "__main__":
    run_demo()