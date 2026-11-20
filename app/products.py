"""Produk catalog. Produksi: ganti dengan Shopee/Tokopedia affiliate API."""

CATALOG: dict[str, list[dict]] = {
    "cleanser": [
        {"nama": "Wardah Lightening Facial Wash", "merek": "Wardah", "harga": "Rp 25.000 – 45.000"},
        {"nama": "Somethinc Low pH Cleanser", "merek": "Somethinc", "harga": "Rp 55.000 – 75.000"},
        {"nama": "Skintific Amino Acid Gentle Cleanser", "merek": "Skintific", "harga": "Rp 65.000 – 90.000"},
        {"nama": "Emina Bright Stuff Facial Wash", "merek": "Emina", "harga": "Rp 20.000 – 35.000"},
        {"nama": "Azarine Hydrasoothe Cleanser", "merek": "Azarine", "harga": "Rp 45.000 – 65.000"},
    ],
    "moisturizer": [
        {"nama": "Skintific 5X Ceramide Barrier Moisturizer", "merek": "Skintific", "harga": "Rp 75.000 – 100.000"},
        {"nama": "Emina Bright Stuff Moisturizing Cream", "merek": "Emina", "harga": "Rp 25.000 – 40.000"},
        {"nama": "Wardah Hydra Rose Moisturizer", "merek": "Wardah", "harga": "Rp 35.000 – 55.000"},
        {"nama": "Avoskin Your Skin Bae Ceramide Moisturizer", "merek": "Avoskin", "harga": "Rp 90.000 – 120.000"},
        {"nama": "Somethinc Hyalufiller Barrier Serum", "merek": "Somethinc", "harga": "Rp 80.000 – 110.000"},
    ],
    "sunscreen": [
        {"nama": "Azarine Hydrasoothe Sunscreen SPF 45", "merek": "Azarine", "harga": "Rp 45.000 – 65.000"},
        {"nama": "Skintific Mineral Sunscreen SPF 50", "merek": "Skintific", "harga": "Rp 80.000 – 110.000"},
        {"nama": "Somethinc Holla UV Mineral Sunscreen SPF 50", "merek": "Somethinc", "harga": "Rp 75.000 – 100.000"},
        {"nama": "Wardah UV Shield Essential Sunscreen SPF 30", "merek": "Wardah", "harga": "Rp 30.000 – 50.000"},
        {"nama": "Scarlett Brightening Sunscreen SPF 35", "merek": "Scarlett", "harga": "Rp 40.000 – 60.000"},
    ],
    "serum": [
        {"nama": "Somethinc 10% Niacinamide Serum", "merek": "Somethinc", "harga": "Rp 60.000 – 85.000"},
        {"nama": "Skintific 10% Niacinamide Serum", "merek": "Skintific", "harga": "Rp 55.000 – 80.000"},
        {"nama": "Avoskin Miraculous Retinol Serum", "merek": "Avoskin", "harga": "Rp 100.000 – 140.000"},
        {"nama": "Wardah Lightening Serum", "merek": "Wardah", "harga": "Rp 45.000 – 65.000"},
        {"nama": "Emina Bright Stuff Serum", "merek": "Emina", "harga": "Rp 30.000 – 50.000"},
    ],
    "toner": [
        {"nama": "Somethinc BHA Pore Cleansing Toner", "merek": "Somethinc", "harga": "Rp 55.000 – 80.000"},
        {"nama": "Avoskin Perfect Hydrating Treatment Essence", "merek": "Avoskin", "harga": "Rp 85.000 – 115.000"},
        {"nama": "Skintific Mugwort Pore Toner", "merek": "Skintific", "harga": "Rp 60.000 – 85.000"},
        {"nama": "Emina Bright Stuff Toner", "merek": "Emina", "harga": "Rp 20.000 – 35.000"},
        {"nama": "Wardah White Secret Toner", "merek": "Wardah", "harga": "Rp 30.000 – 50.000"},
    ],
    "niacinamide": [
        {"nama": "Somethinc 10% Niacinamide Serum", "merek": "Somethinc", "harga": "Rp 60.000 – 85.000"},
        {"nama": "Skintific 10% Niacinamide Serum", "merek": "Skintific", "harga": "Rp 55.000 – 80.000"},
        {"nama": "Azarine Niacinamide Brightening Serum", "merek": "Azarine", "harga": "Rp 45.000 – 65.000"},
    ],
    "vitamin_c": [
        {"nama": "Avoskin Your Skin Bae Vitamin C Serum", "merek": "Avoskin", "harga": "Rp 95.000 – 125.000"},
        {"nama": "Somethinc Level 1% C+Ferulic+Peptide", "merek": "Somethinc", "harga": "Rp 75.000 – 100.000"},
        {"nama": "Scarlett Brightening Vitamin C Serum", "merek": "Scarlett", "harga": "Rp 55.000 – 80.000"},
    ],
    "retinol": [
        {"nama": "Avoskin Miraculous Refining Treatment Serum", "merek": "Avoskin", "harga": "Rp 100.000 – 140.000"},
        {"nama": "Somethinc Bakuchiol 1% + Retinol 0.1%", "merek": "Somethinc", "harga": "Rp 85.000 – 115.000"},
    ],
    "eye_cream": [
        {"nama": "Skintific Eye Cream Dark Circle", "merek": "Skintific", "harga": "Rp 70.000 – 95.000"},
        {"nama": "Somethinc Eye Cream Peptide", "merek": "Somethinc", "harga": "Rp 80.000 – 110.000"},
    ],
    "exfoliator": [
        {"nama": "Somethinc AHA BHA Exfoliating Toner", "merek": "Somethinc", "harga": "Rp 60.000 – 85.000"},
        {"nama": "Avoskin Miraculous AHA BHA Toner", "merek": "Avoskin", "harga": "Rp 90.000 – 125.000"},
        {"nama": "Skintific AHA BHA Exfoliating Toner", "merek": "Skintific", "harga": "Rp 65.000 – 90.000"},
    ],
    "face_mask": [
        {"nama": "Skintific Mugwort Pore Mask", "merek": "Skintific", "harga": "Rp 55.000 – 75.000"},
        {"nama": "Somethinc Mugwort Acne Clay Mask", "merek": "Somethinc", "harga": "Rp 65.000 – 90.000"},
        {"nama": "Emina Bright Stuff Sheet Mask", "merek": "Emina", "harga": "Rp 15.000 – 25.000"},
    ],
    "lip": [
        {"nama": "Emina Lip Scrub", "merek": "Emina", "harga": "Rp 20.000 – 30.000"},
        {"nama": "Wardah Lip Moisture", "merek": "Wardah", "harga": "Rp 15.000 – 25.000"},
    ],
}

# Canonical names first — exact match wins before partial fallback.
KEYWORD_MAP: list[tuple[str, str]] = [
    # exact canonical → catalog key
    ("serum niacinamide", "niacinamide"),
    ("serum vitamin c", "vitamin_c"),
    ("serum retinol", "retinol"),
    ("eye cream", "eye_cream"),
    ("exfoliator", "exfoliator"),
    ("face mask", "face_mask"),
    ("lip care", "lip"),
    ("cleanser", "cleanser"),
    ("moisturizer", "moisturizer"),
    ("sunscreen", "sunscreen"),
    ("toner", "toner"),
    # fallback partial matches (untuk input bebas di luar canonical)
    ("niacinamide", "niacinamide"),
    ("vitamin c", "vitamin_c"),
    ("retinol", "retinol"),
    ("mata", "eye_cream"),
    ("exfoliat", "exfoliator"),
    ("aha", "exfoliator"),
    ("bha", "exfoliator"),
    ("scrub", "exfoliator"),
    ("mask", "face_mask"),
    ("masker", "face_mask"),
    ("sabun", "cleanser"),
    ("facial wash", "cleanser"),
    ("pembersih", "cleanser"),
    ("pelembab", "moisturizer"),
    ("moisturizing", "moisturizer"),
    ("spf", "sunscreen"),
    ("tabir", "sunscreen"),
    ("serum", "serum"),
    ("essence", "toner"),
    ("lip", "lip"),
    ("bibir", "lip"),
]

DEFAULT_PICK = {
    "nama": "Somethinc Hyalufiller Barrier Serum",
    "merek": "Somethinc",
    "harga": "Rp 80.000 – 110.000",
    "untuk": "hidrasi umum",
    "alasan": "Cocok untuk menjaga kelembapan kulit sepanjang hari",
}

_pick_counters: dict[str, int] = {}  # rotasi produk per kategori (single-instance)


def curate(categories: list[dict], limit: int = 4) -> list[dict]:
    """Map kategori dari Gemini ke produk nyata. Rotasi produk tiap request."""
    picks = []
    seen_keys: set[str] = set()

    for cat in categories[:limit]:
        label = cat.get("kategori", "").lower()
        key = next(
            (catalog_key for kw, catalog_key in KEYWORD_MAP if kw in label),
            None,
        )
        if key is None or key in seen_keys:
            continue
        seen_keys.add(key)

        products = CATALOG.get(key, [])
        if not products:
            continue

        idx = _pick_counters.get(key, 0) % len(products)
        _pick_counters[key] = idx + 1

        picks.append({
            **products[idx],
            "untuk": cat.get("kategori"),
            "alasan": cat.get("alasan", ""),
        })

    return picks or [DEFAULT_PICK]
