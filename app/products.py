"""Kurasi produk contoh untuk demo monetisasi afiliasi.

Di versi produksi, modul ini diganti jadi client ke API afiliasi e-commerce
sungguhan (mis. Tokopedia/Shopee affiliate), idealnya dengan caching supaya
tidak query berulang untuk kategori yang sama.
"""

CATALOG: dict[str, dict[str, str]] = {
    "cleanser": {"nama": "Facial Wash Gentle (contoh)", "harga": "Rp35.000 - 60.000"},
    "moisturizer": {"nama": "Moisturizer Ringan (contoh)", "harga": "Rp45.000 - 90.000"},
    "sunscreen": {"nama": "Sunscreen SPF 30+ (contoh)", "harga": "Rp50.000 - 120.000"},
    "serum": {"nama": "Serum Niacinamide (contoh)", "harga": "Rp40.000 - 85.000"},
    "toner": {"nama": "Toner Hydrating (contoh)", "harga": "Rp35.000 - 70.000"},
}

DEFAULT_PICK = {"nama": "Moisturizer Ringan (contoh)", "harga": "Rp45.000 - 90.000", "untuk": "umum"}


def curate(categories: list[dict], limit: int = 3) -> list[dict]:
    """Mapping sederhana nama kategori -> contoh produk."""
    picks = []
    for cat in categories[:limit]:
        label = cat.get("kategori", "").lower()
        key = next((k for k in CATALOG if k in label), None)
        if key:
            picks.append({**CATALOG[key], "untuk": cat.get("kategori")})
    return picks or [DEFAULT_PICK]
