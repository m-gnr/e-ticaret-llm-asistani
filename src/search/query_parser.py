import re
from dataclasses import dataclass, asdict, field
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
    attribute_filters: dict[str, str | int | float | bool] = field(default_factory=dict)

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
        "göster",
        "goster",
        "listele",
        "tavsiye",
        "satın al",
        "satin al",
        "kulaklık",
        "kulaklik",
        "mouse",
        "klavye",
        "laptop",
        "bilgisayar",
        "tablet",
        "telefon",
        "iphone",
        "galaxy",
        "monitör",
        "monitor",
        "powerbank",
        "sweatshirt",
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
    "Telefon": ["telefon", "akıllı telefon", "akilli telefon", "iphone", "galaxy"],
    "Tablet": ["tablet"],
    "Monitör": ["monitör", "monitor"],
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


BRAND_ALIASES = {
    "iphone": "apple",
    "apple": "apple",
    "samsung": "samsung",
    "galaxy": "samsung",
    "xiaomi": "xiaomi",
    "sony": "sony",
    "jbl": "jbl",
    "razer": "razer",
    "logitech": "logitech",
    "philips": "philips",
    "arzum": "arzum",
    "monster": "monster",
    "lenovo": "lenovo",
    "asus": "asus",
    "msi": "msi",
    "hp": "hp",
    "dell": "dell",
    "anker": "anker",
    "huawei": "huawei",
    "kingston": "kingston",
    "corsair": "corsair",
    "dyson": "dyson",
    "nike": "nike",
    "adidas": "adidas",
    "puma": "puma",
    "lc waikiki": "lc waikiki",
    "mavi": "mavi",
    "defacto": "defacto",
}


COLOR_VALUES = {
    "siyah": "Siyah",
    "beyaz": "Beyaz",
    "mavi": "Mavi",
    "pembe": "Pembe",
    "gri": "Gri",
    "kırmızı": "Kırmızı",
    "kirmizi": "Kırmızı",
    "yeşil": "Yeşil",
    "yesil": "Yeşil",
    "kahverengi": "Kahverengi",
    "gümüş": "Gümüş",
    "gumus": "Gümüş",
}


ATTRIBUTE_PATTERNS = [
    {
        "key": "ram",
        "regex_patterns": [
            r"\b(\d+)\s*gb\s*ram\b",
            r"\bram\s*(\d+)\s*gb\b",
        ],
        "value_format": "{n}GB",
    },
    {
        "key": "depolama",
        "regex_patterns": [r"\b(\d+)\s*gb\b"],
        "value_format": "{n}GB",
        "context_keywords": [
            "iphone",
            "telefon",
            "galaxy",
            "tablet",
            "akıllı telefon",
            "akilli telefon",
        ],
        "exclude_near_keywords": ["ram"],
    },
    {
        "key": "baglanti",
        "keyword_values": {
            "bluetooth": "Bluetooth",
            "kablosuz": "Bluetooth",
            "kablolu": "Kablolu",
        },
    },
    {
        "key": "renk",
        "keyword_values": COLOR_VALUES,
    },
    {
        "key": "yenileme_hizi",
        "regex_patterns": [r"\b(\d+)\s*hz\b"],
        "value_format": "{n}Hz",
    },
    {
        "key": "ekran_boyutu",
        "regex_patterns": [r"\b(\d+(?:[.,]\d+)?)\s*(inç|inch|inc)\b"],
        "value_format": "{n} inç",
    },
    {
        "key": "kapasite",
        "regex_patterns": [r"\b(\d+)\s*mah\b"],
        "value_format": "{n} mAh",
    },
    {
        "key": "oyuncu",
        "keyword_values": {
            "oyuncu": True,
            "gaming": True,
        },
    },
    {
        "key": "kumas",
        "keyword_values": {
            "pamuklu": "Pamuk",
            "pamuk": "Pamuk",
            "denim": "Denim",
        },
        "context_keywords": [
            "tişört",
            "tisort",
            "tshirt",
            "t-shirt",
            "gömlek",
            "gomlek",
            "sweatshirt",
            "pantolon",
        ],
    },
]


CLOTHING_CONTEXT_KEYWORDS = [
    "tişört",
    "tisort",
    "tshirt",
    "t-shirt",
    "gömlek",
    "gomlek",
    "sweatshirt",
    "pantolon",
    "mont",
]


SHOE_CONTEXT_KEYWORDS = [
    "ayakkabı",
    "ayakkabi",
    "ayakkabılar",
    "ayakkabilar",
    "sneaker",
    "bot",
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


def normalize_query_text(text: str) -> str:
    """
    Sorguyu attribute çıkarımı için küçük harfe indirir ve fazla boşlukları temizler.
    """
    return re.sub(r"\s+", " ", normalize_text(text))


def normalize_attribute_value(value: Any) -> str | int | float | bool:
    """
    Attribute değerlerini metadata'daki yazıma yakın, sade bir forma getirir.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value

    if value is None:
        return ""

    return str(value).strip()


def has_any_keyword(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def match_has_excluded_context(text: str, start: int, end: int, keywords: list[str]) -> bool:
    nearby_text = text[max(0, start - 8) : min(len(text), end + 8)]
    return any(keyword in nearby_text for keyword in keywords)


def format_regex_attribute_value(match: re.Match[str], value_format: str) -> str:
    raw_number = match.group(1).replace(",", ".")
    number = raw_number[:-2] if raw_number.endswith(".0") else raw_number
    return value_format.format(n=number)


def extract_beden_filter(text: str) -> str | None:
    patterns = [
        r"\b(xs|s|m|l|xl|xxl)\s*beden\b",
        r"\bbeden\s*(xs|s|m|l|xl|xxl)\b",
        r"\b(xs|s|m|l|xl|xxl)\s*(tişört|tisort|tshirt|t-shirt|gömlek|gomlek|sweatshirt|pantolon)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).upper()

    if has_any_keyword(text, CLOTHING_CONTEXT_KEYWORDS):
        match = re.search(r"\b(xs|s|m|l|xl|xxl)\b", text)
        if match:
            return match.group(1).upper()

    return None


def extract_numara_filter(text: str) -> str | None:
    patterns = [
        r"\b(\d{2})\s*numara\b",
        r"\bnumara\s*(\d{2})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    if has_any_keyword(text, SHOE_CONTEXT_KEYWORDS):
        match = re.search(r"\b(3[5-9]|4[0-9])\b", text)
        if match:
            return match.group(1)

    return None


def extract_attribute_filters(query: str) -> dict[str, str | int | float | bool]:
    """
    Sorgudaki ürün özelliklerini semantic_index.metadata.ozellikler alanına
    uygulanabilecek filtrelere dönüştürür.
    """
    text = normalize_query_text(query)
    filters: dict[str, str | int | float | bool] = {}

    for definition in ATTRIBUTE_PATTERNS:
        key = definition["key"]
        context_keywords = definition.get("context_keywords")

        if context_keywords and not has_any_keyword(text, context_keywords):
            continue

        for keyword, value in definition.get("keyword_values", {}).items():
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                filters[key] = normalize_attribute_value(value)
                break

        if key in filters:
            continue

        for pattern in definition.get("regex_patterns", []):
            match = re.search(pattern, text)
            if not match:
                continue

            exclude_keywords = definition.get("exclude_near_keywords", [])
            if exclude_keywords and match_has_excluded_context(
                text,
                match.start(),
                match.end(),
                exclude_keywords,
            ):
                continue

            value_format = definition.get("value_format", "{n}")
            filters[key] = normalize_attribute_value(
                format_regex_attribute_value(match, value_format)
            )
            break

    beden = extract_beden_filter(text)
    if beden is not None:
        filters["beden"] = beden

    numara = extract_numara_filter(text)
    if numara is not None:
        filters["numara"] = numara

    return filters


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
    for keyword, brand in BRAND_ALIASES.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
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
    attribute_filters = extract_attribute_filters(normalized)
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
        attribute_filters=attribute_filters,
    )


def run_demo() -> None:
    test_queries = [
        "iphone 64 gb",
        "iphone 128 gb",
        "samsung galaxy 128 gb",
        "bluetooth kulaklık",
        "kablolu oyuncu mouse",
        "siyah kulaklık",
        "27 inç 165hz monitör",
        "20000 mah powerbank",
        "16 gb ram laptop",
        "stokta siyah bluetooth kulaklık",
        "1000 TL altı stokta olan kablosuz kulaklık öner",
        "s beden tişört",
        "m beden siyah tişört",
        "xl sweatshirt",
        "42 numara ayakkabı",
        "41 ayakkabı",
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
