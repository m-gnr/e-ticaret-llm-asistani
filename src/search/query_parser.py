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
    max_rating: int | None = None
    rating_equals: int | None = None
    category: str | None = None
    brand: str | None = None
    status: str | None = None
    model_filter: str | None = None
    sort_by: str | None = None
    sort_direction: str | None = None
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
        "samsung",
        "galaxy",
        "xiaomi",
        "redmi",
        "poco",
        "oppo",
        "vivo",
        "realme",
        "honor",
        "macbook",
        "notebook",
        "ultrabook",
        "thinkpad",
        "ideapad",
        "vivobook",
        "zenbook",
        "victus",
        "nitro",
        "monster",
        "msi",
        "monitör",
        "monitor",
        "powerbank",
        "sweatshirt",
        "sweat",
        "gömlek",
        "gomlek",
        "pantolon",
        "jean",
        "chino",
        "mont",
        "parka",
        "bot",
        "sneaker",
        "airpods",
        "buds",
        "ayakkabı",
        "ayakkabi",
        "tişört",
        "tisort",
        "tshirt",
        "t-shirt",
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
    "Bot": ["outdoor bot", "bot"],

    # Genel kategoriler
    "Kulaklık": [
        "kulaklık",
        "kulaklik",
        "bluetooth kulaklık",
        "kablosuz kulaklık",
        "airpods",
        "buds",
    ],
    "Mouse": ["mouse", "fare", "kablosuz mouse"],
    "Klavye": ["klavye", "keyboard", "kablosuz klavye"],
    "Laptop": [
        "laptop",
        "dizüstü",
        "dizustu",
        "notebook",
        "ultrabook",
        "macbook",
        "thinkpad",
        "ideapad",
        "vivobook",
        "zenbook",
        "victus",
        "nitro",
        "monster",
        "msi",
    ],
    "Telefon": [
        "telefon",
        "akıllı telefon",
        "akilli telefon",
        "iphone",
        "samsung",
        "galaxy",
        "xiaomi",
        "redmi",
        "poco",
        "oppo",
        "vivo",
        "realme",
        "honor",
    ],
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
    "Tişört": ["tişört", "tisort", "tshirt", "t-shirt"],
    "Gömlek": ["gömlek", "gomlek"],
    "Pantolon": ["pantolon", "jean", "chino"],
    "Sweatshirt": ["sweatshirt", "sweat", "kapüşonlu", "kapusonlu"],
    "Mont": ["şişme mont", "sisme mont", "kışlık mont", "kislik mont", "parka", "mont"],
    "Ayakkabı": ["ayakkabı", "ayakkabi", "ayakkabılar", "ayakkabilar", "sneaker"],
}


BRAND_ALIASES = {
    "new balance": "new balance",
    "lc waikiki": "lc waikiki",
    "iphone": "apple",
    "macbook": "apple",
    "apple": "apple",
    "samsung": "samsung",
    "galaxy": "samsung",
    "redmi": "xiaomi",
    "xiaomi": "xiaomi",
    "poco": "poco",
    "oppo": "oppo",
    "vivo": "vivo",
    "realme": "realme",
    "honor": "honor",
    "sony": "sony",
    "jbl": "jbl",
    "razer": "razer",
    "logitech": "logitech",
    "philips": "philips",
    "arzum": "arzum",
    "monster": "monster",
    "thinkpad": "lenovo",
    "ideapad": "lenovo",
    "lenovo": "lenovo",
    "vivobook": "asus",
    "zenbook": "asus",
    "tuf": "asus",
    "asus": "asus",
    "victus": "hp",
    "hp": "hp",
    "xps": "dell",
    "dell": "dell",
    "nitro": "acer",
    "acer": "acer",
    "msi": "msi",
    "anker": "anker",
    "huawei": "huawei",
    "kingston": "kingston",
    "corsair": "corsair",
    "dyson": "dyson",
    "nike": "nike",
    "adidas": "adidas",
    "puma": "puma",
    "levi's": "levi's",
    "levis": "levi's",
    "skechers": "skechers",
    "converse": "converse",
    "columbia": "columbia",
    "koton": "koton",
    "mavi": "mavi",
    "defacto": "defacto",
}


COLOR_VALUES = {
    "siyah": "Siyah",
    "beyaz": "Beyaz",
    "gri": "Gri",
    "mavi": "Mavi",
    "lacivert": "Lacivert",
    "kırmızı": "Kırmızı",
    "kirmizi": "Kırmızı",
    "yeşil": "Yeşil",
    "yesil": "Yeşil",
    "bordo": "Bordo",
    "haki": "Haki",
    "bej": "Bej",
    "mor": "Mor",
    "pembe": "Pembe",
    "altın": "Altın",
    "altin": "Altın",
    "sarı": "Sarı",
    "sari": "Sarı",
    "kahverengi": "Kahverengi",
    "gümüş": "Gümüş",
    "gumus": "Gümüş",
}


PHONE_CONTEXT_KEYWORDS = [
    "iphone",
    "samsung",
    "galaxy",
    "xiaomi",
    "redmi",
    "poco",
    "oppo",
    "vivo",
    "realme",
    "honor",
    "telefon",
]


LAPTOP_CONTEXT_KEYWORDS = [
    "laptop",
    "notebook",
    "ultrabook",
    "macbook",
    "thinkpad",
    "ideapad",
    "vivobook",
    "zenbook",
    "victus",
    "nitro",
    "monster",
    "msi",
]


MODEL_PATTERNS = [
    # Telefon modelleri
    (r"\biphone\s+se\s+2022\b", "iPhone SE 2022"),
    (r"\biphone\s+se\b", "iPhone SE"),
    (r"\biphone\s+(11|12|13|14|15)\b", "iPhone {g1}"),
    (r"\b(?:samsung\s+|galaxy\s+)?s21\s*fe\b", "Galaxy S21 FE"),
    (r"\b(?:samsung\s+|galaxy\s+)a15\b", "Galaxy A15"),
    (r"\b(?:samsung\s+|galaxy\s+)a35\b", "Galaxy A35"),
    (r"\b(?:samsung\s+|galaxy\s+)a55\b", "Galaxy A55"),
    (r"\b(?:samsung\s+|galaxy\s+)s23\b", "Galaxy S23"),
    (r"\b(?:samsung\s+|galaxy\s+)s24\b", "Galaxy S24"),
    (r"\bredmi\s+note\s+13\s+pro\b", "Redmi Note 13 Pro"),
    (r"\bredmi\s+note\s+12\b", "Redmi Note 12"),
    (r"\bredmi\s+note\s+13\b", "Redmi Note 13"),
    (r"\bxiaomi\s+13t\b", "Xiaomi 13T"),
    (r"\bpoco\s+x5\s+pro\b", "Poco X5 Pro"),
    (r"\bpoco\s+x6\s+pro\b", "Poco X6 Pro"),
    (r"\boppo\s+reno\s+10\b", "Oppo Reno 10"),
    (r"\boppo\s+a78\b", "Oppo A78"),
    (r"\bvivo\s+v29\b", "Vivo V29"),
    (r"\bvivo\s+y36\b", "Vivo Y36"),
    (r"\brealme\s+11\s+pro\b", "Realme 11 Pro"),
    (r"\brealme\s+c55\b", "Realme C55"),
    (r"\bhonor\s+90\b", "Honor 90"),
    (r"\bhonor\s+x9a\b", "Honor X9a"),

    # Laptop modelleri
    (r"\bmacbook\s+pro\s+14\s+m3\b", "MacBook Pro 14 M3"),
    (r"\bmacbook\s+air\s+m1\b", "MacBook Air M1"),
    (r"\bmacbook\s+air\s+m2\b", "MacBook Air M2"),
    (r"\bideapad\s+15\b", "IdeaPad 15"),
    (r"\bthinkpad\s+e14\b", "ThinkPad E14"),
    (r"\blegion\s+5\b", "Legion 5"),
    (r"\btuf\s+gaming\s+a15\b", "TUF Gaming A15"),
    (r"\bvivobook\s+15\b", "Vivobook 15"),
    (r"\bzenbook\s+14\b", "Zenbook 14"),
    (r"\bpavilion\s+15\b", "Pavilion 15"),
    (r"\bvictus\s+16\b", "Victus 16"),
    (r"\benvy\s+x360\b", "Envy x360"),
    (r"\binspiron\s+15\b", "Inspiron 15"),
    (r"\bxps\s+13\b", "XPS 13"),
    (r"\bdell\s+g15\b", "G15"),
    (r"\baspire\s+5\b", "Aspire 5"),
    (r"\bnitro\s+5\b", "Nitro 5"),
    (r"\bswift\s+3\b", "Swift 3"),
    (r"\bthin\s+gf63\b", "Thin GF63"),
    (r"\bkatana\s+15\b", "Katana 15"),
    (r"\bmatebook\s+d15\b", "MateBook D15"),
    (r"\bmatebook\s+14\b", "MateBook 14"),
    (r"\babra\s+a5\b", "Abra A5"),
    (r"\btulpar\s+t7\b", "Tulpar T7"),
]


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
        "regex_patterns": [
            r"\b(\d+)\s*gb\s*ssd\b",
        ],
        "value_format": "{n}GB SSD",
        "context_keywords": LAPTOP_CONTEXT_KEYWORDS,
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


SORT_PATTERNS = [
    ("rating", "asc", ["düşük puanlı", "dusuk puanli", "düşük yıldızlı", "dusuk yildizli", "kötü yorumlar", "kotu yorumlar", "en kötü yorumlar", "en kotu yorumlar", "olumsuz yorumlar", "kötü puanlı", "kotu puanli", "az puanlı", "az puanli"]),
    ("rating", "desc", ["yüksek puanlı", "yuksek puanli", "iyi yorumlar", "en iyi yorumlar", "olumlu yorumlar", "iyi puanlı", "iyi puanli", "çok beğenilen", "cok begenilen"]),
    ("price", "desc", ["en pahalı", "pahalı", "yüksek fiyatlı", "yuksek fiyatli", "fiyatı yüksek", "fiyati yuksek"]),
    ("price", "asc", ["en ucuz", "ucuz", "uygun fiyatlı", "uygun fiyatli", "düşük fiyatlı", "dusuk fiyatli"]),
]


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


def parse_price_number(value: str) -> float:
    normalized = value.replace(".", "").replace(",", ".")
    return float(normalized)


def extract_price_range(text: str) -> tuple[float | None, float | None]:
    number = r"(\d+(?:[.,]\d{3})*(?:[.,]\d+)?)"
    patterns = [
        rf"{number}\s+{number}\s*tl\s*arası",
        rf"{number}\s*tl\s+ile\s+{number}\s*tl\s*arası",
        rf"{number}\s*-\s*{number}\s*tl\s*arası",
        rf"{number}\s*den\s+{number}\s*e\s*kadar",
        rf"{number}\s*'den\s+{number}\s*'e\s*kadar",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            first = parse_price_number(match.group(1))
            second = parse_price_number(match.group(2))
            return min(first, second), max(first, second)

    return None, None


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


def extract_pantolon_beden_filter(text: str) -> str | None:
    if "pantolon" not in text and "jean" not in text and "chino" not in text:
        return None

    slash_match = re.search(r"\b(30|32|34|36)/(30|32|34|36)\b", text)
    if slash_match:
        return slash_match.group(0)

    explicit_match = re.search(r"\b(30|32|34|36)\s*beden\s+(?:mavi\s+|siyah\s+|gri\s+|bej\s+|lacivert\s+)?(?:pantolon|jean|chino)\b", text)
    if explicit_match:
        return explicit_match.group(1)

    reverse_match = re.search(r"\b(?:pantolon|jean|chino)\s+(?:beden\s*)?(30|32|34|36)\b", text)
    if reverse_match:
        return reverse_match.group(1)

    bare_match = re.search(r"\b(30|32|34|36)\b", text)
    if bare_match:
        return bare_match.group(1)

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


def detect_model_filter(text: str) -> str | None:
    for pattern, model_name in MODEL_PATTERNS:
        match = re.search(pattern, text)
        if not match:
            continue

        if "{g1}" in model_name:
            return model_name.format(g1=match.group(1))

        return model_name

    return None


def infer_category_from_model_filter(model_filter: str | None) -> str | None:
    if model_filter is None:
        return None

    phone_prefixes = (
        "iPhone",
        "Galaxy",
        "Redmi",
        "Xiaomi",
        "Poco",
        "Oppo",
        "Vivo",
        "Realme",
        "Honor",
    )
    laptop_prefixes = (
        "MacBook",
        "IdeaPad",
        "ThinkPad",
        "Legion",
        "TUF",
        "Vivobook",
        "Zenbook",
        "Pavilion",
        "Victus",
        "Envy",
        "Inspiron",
        "XPS",
        "G15",
        "Aspire",
        "Nitro",
        "Swift",
        "Thin",
        "Katana",
        "MateBook",
        "Abra",
        "Tulpar",
    )

    if model_filter.startswith(phone_prefixes):
        return "Telefon"

    if model_filter.startswith(laptop_prefixes):
        return "Laptop"

    return None


def extract_contextual_gb_filters(text: str) -> dict[str, str]:
    filters: dict[str, str] = {}
    phone_context = has_any_keyword(text, PHONE_CONTEXT_KEYWORDS)
    laptop_context = has_any_keyword(text, LAPTOP_CONTEXT_KEYWORDS)

    ram_match = re.search(r"\b(\d+)\s*gb\s*ram\b|\bram\s*(\d+)\s*gb\b", text)
    if ram_match:
        ram_value = ram_match.group(1) or ram_match.group(2)
        filters["ram"] = f"{ram_value}GB"

    gb_ssd_match = re.search(r"\b(\d+)\s*gb\s*ssd\b", text)
    if gb_ssd_match and laptop_context:
        filters["depolama"] = f"{gb_ssd_match.group(1)}GB SSD"

    tb_ssd_match = re.search(r"\b(\d+)\s*tb\s*ssd\b", text)
    if tb_ssd_match and laptop_context:
        filters["depolama"] = f"{tb_ssd_match.group(1)}TB SSD"

    bare_gb_match = re.search(r"\b(\d+)\s*gb\b", text)
    if not bare_gb_match:
        return filters

    bare_gb_value = bare_gb_match.group(1)
    if phone_context and not ram_match:
        filters["depolama"] = f"{bare_gb_value}GB"
    elif laptop_context and "depolama" not in filters and not ram_match:
        if bare_gb_value in {"4", "8", "16", "32"}:
            filters["ram"] = f"{bare_gb_value}GB"
        else:
            filters["depolama"] = f"{bare_gb_value}GB SSD"

    return filters


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

    pantolon_beden = extract_pantolon_beden_filter(text)
    if pantolon_beden is not None:
        filters["beden"] = pantolon_beden

    numara = extract_numara_filter(text)
    if numara is not None:
        filters["numara"] = numara

    filters.update(extract_contextual_gb_filters(text))

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
        r"\b([1-5])\s*(puan|yıldız|yildiz)\s*üstü\b",
        r"\b([1-5])\s*(puan|yıldız|yildiz)\s*ve\s*üzeri\b",
        r"\b([1-5])\s*(puan|yıldız|yildiz)\s*üzeri\b",
        r"en az\s*([1-5])\s*(puan|yıldız|yildiz)",
        r"minimum\s*([1-5])\s*(puan|yıldız|yildiz)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    high_rating_keywords = [
        "yüksek puanlı",
        "yuksek puanli",
        "iyi yorumlar",
        "en iyi yorumlar",
        "olumlu yorumlar",
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


def extract_max_rating(text: str) -> int | None:
    patterns = [
        r"\b([1-5])\s*(puan|yıldız|yildiz)\s*altı\b",
        r"\b([1-5])\s*(puan|yıldız|yildiz)\s*ve\s*altı\b",
        r"\b([1-5])\s*(puan|yıldız|yildiz)\s*altında\b",
        r"en fazla\s*([1-5])\s*(puan|yıldız|yildiz)",
        r"maksimum\s*([1-5])\s*(puan|yıldız|yildiz)",
        r"max\s*([1-5])\s*(puan|yıldız|yildiz)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    low_rating_keywords = [
        "düşük puanlı",
        "dusuk puanli",
        "düşük yıldızlı",
        "dusuk yildizli",
        "kötü yorumlar",
        "kotu yorumlar",
        "en kötü yorumlar",
        "en kotu yorumlar",
        "olumsuz yorumlar",
        "kötü puanlı",
        "kotu puanli",
        "olumsuz yorumlu",
        "az puanlı",
        "az puanli",
    ]

    if any(keyword in text for keyword in low_rating_keywords):
        return 2

    return None


def extract_rating_equals(text: str) -> int | None:
    patterns = [
        r"\b([1-5])\s*(puan|yıldız|yildiz)\s+(yorum|yorumlar|değerlendirme|degerlendirme)\b",
        r"\b([1-5])\s*(puan|yıldız|yildiz)\s*$",
        r"\b([1-5])\s*(puanlı|puanli|yıldızlı|yildizli)\s*(yorum|yorumlar)?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    return None


def detect_intent(text: str) -> str | None:
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return intent

    return None


def detect_category(text: str) -> str | None:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords):
            return category

    return None


def detect_brand(text: str) -> str | None:
    for keyword, brand in BRAND_ALIASES.items():
        if keyword == "mavi" and has_any_keyword(text, CLOTHING_CONTEXT_KEYWORDS):
            if not re.search(r"\bmavi\s+(marcus|oversize|marka)\b", text):
                continue

        if re.search(rf"\b{re.escape(keyword)}\b", text):
            return brand

    return None


def detect_status(text: str) -> str | None:
    for status, keywords in STATUS_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return status

    return None


def detect_sort_intent(text: str) -> tuple[str | None, str | None]:
    for sort_by, sort_direction, keywords in SORT_PATTERNS:
        if any(keyword in text for keyword in keywords):
            return sort_by, sort_direction

    return None, None


def clean_search_text(text: str) -> str:
    cleaned = text

    remove_patterns = [
        r"\d+(?:[.,]\d+)?\s*tl\s*altı",
        r"\d+(?:[.,]\d+)?\s*tl\s*altında",
        r"\d+(?:[.,]\d+)?\s*tl\s*aşağısı",
        r"\d+(?:[.,]\d+)?\s*tl\s*ye\s*kadar",
        r"\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s+\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*tl\s*arası",
        r"\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*tl\s+ile\s+\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*tl\s*arası",
        r"\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*-\s*\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*tl\s*arası",
        r"\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*den\s+\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*e\s*kadar",
        r"\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*'den\s+\d+(?:[.,]\d{3})*(?:[.,]\d+)?\s*'e\s*kadar",
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
        r"en pahalı",
        r"pahalı",
        r"yüksek fiyatlı",
        r"yuksek fiyatli",
        r"fiyatı yüksek",
        r"fiyati yuksek",
        r"en ucuz",
        r"ucuz",
        r"uygun fiyatlı",
        r"uygun fiyatli",
        r"düşük fiyatlı",
        r"dusuk fiyatli",
    ]

    for pattern in remove_patterns:
        cleaned = re.sub(pattern, " ", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def parse_query(query: str) -> ParsedQuery:
    normalized = normalize_text(query)

    range_min_price, range_max_price = extract_price_range(normalized)
    max_price = range_max_price if range_max_price is not None else extract_max_price(normalized)
    min_price = range_min_price if range_min_price is not None else extract_min_price(normalized)
    in_stock_only, out_of_stock_only = extract_stock_filter(normalized)
    rating_equals = extract_rating_equals(normalized)
    min_rating = None if rating_equals is not None else extract_min_rating(normalized)
    max_rating = None if rating_equals is not None else extract_max_rating(normalized)
    category = detect_category(normalized)
    brand = detect_brand(normalized)
    status = detect_status(normalized)
    model_filter = detect_model_filter(normalized)
    if category is None:
        category = infer_category_from_model_filter(model_filter)

    attribute_filters = extract_attribute_filters(normalized)
    search_text = clean_search_text(normalized)
    intent = detect_intent(normalized)
    if intent is None and (category or brand or model_filter or attribute_filters):
        intent = "product"

    source_tables = INTENT_TABLES.get(intent, [])
    sort_by, sort_direction = detect_sort_intent(normalized)

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
        max_rating=max_rating,
        rating_equals=rating_equals,
        category=category,
        brand=brand,
        status=status,
        model_filter=model_filter,
        sort_by=sort_by,
        sort_direction=sort_direction,
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
        "l beden lacivert tişört",
        "bordo sweatshirt",
        "haki mont",
        "lacivert gömlek",
        "poco 512 gb",
        "iphone 15 mavi",
        "iphone 13 256 gb mavi",
        "samsung s23 gri",
        "samsung s24 siyah",
        "redmi note 13 pro",
        "poco x6 pro 512 gb",
        "macbook 8 gb",
        "macbook air m2 8 gb",
        "macbook pro 14 m3 16 gb",
        "lenovo legion 5 32 gb ram",
        "hp victus 16 oyuncu laptop",
        "dell xps 13 ultrabook",
        "acer nitro 5 oyuncu laptop",
        "512 gb ssd laptop",
        "16 gb ram laptop",
        "32 beden mavi pantolon",
        "32/32 mavi pantolon",
        "34/32 mavi pantolon",
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
