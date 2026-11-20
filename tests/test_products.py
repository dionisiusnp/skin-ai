import pytest

from app.products import CATALOG, curate


# ── Positive ──────────────────────────────────────────────────────────────────

def test_curate_canonical_cleanser():
    picks = curate([{"kategori": "cleanser", "alasan": "kulit sensitif"}])
    assert picks[0]["untuk"] == "cleanser"
    assert picks[0]["nama"] in [p["nama"] for p in CATALOG["cleanser"]]


def test_curate_canonical_serum_niacinamide():
    picks = curate([{"kategori": "serum niacinamide", "alasan": "pori besar"}])
    assert picks[0]["nama"] in [p["nama"] for p in CATALOG["niacinamide"]]


def test_curate_canonical_serum_vitamin_c():
    picks = curate([{"kategori": "serum vitamin C", "alasan": "kusam"}])
    assert picks[0]["nama"] in [p["nama"] for p in CATALOG["vitamin_c"]]


def test_curate_multiple_categories():
    cats = [
        {"kategori": "cleanser", "alasan": "a"},
        {"kategori": "sunscreen", "alasan": "b"},
        {"kategori": "moisturizer", "alasan": "c"},
    ]
    picks = curate(cats)
    assert len(picks) == 3
    untuks = [p["untuk"] for p in picks]
    assert "cleanser" in untuks
    assert "sunscreen" in untuks
    assert "moisturizer" in untuks


def test_curate_respects_limit():
    cats = [{"kategori": k, "alasan": "x"} for k in ["cleanser", "sunscreen", "moisturizer", "toner", "exfoliator"]]
    picks = curate(cats, limit=2)
    assert len(picks) == 2


def test_curate_product_has_required_fields():
    picks = curate([{"kategori": "sunscreen", "alasan": "UV"}])
    p = picks[0]
    assert "nama" in p
    assert "merek" in p
    assert "harga" in p
    assert "untuk" in p


# ── Negative ─────────────────────────────────────────────────────────────────

def test_curate_unknown_category_returns_default():
    picks = curate([{"kategori": "obat ajaib", "alasan": "x"}])
    assert picks  # never empty
    assert picks[0]["nama"]  # has a name


def test_curate_empty_input_returns_default():
    picks = curate([])
    assert picks
    assert len(picks) == 1


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_curate_deduplicates_same_category():
    """Same catalog key appearing twice → only one product returned."""
    cats = [
        {"kategori": "cleanser", "alasan": "a"},
        {"kategori": "cleanser lembut", "alasan": "b"},  # also matches cleanser
    ]
    picks = curate(cats)
    catalog_keys_used = [p["untuk"] for p in picks]
    cleanser_picks = [u for u in catalog_keys_used if "cleanser" in u.lower()]
    assert len(cleanser_picks) == 1


def test_curate_partial_keyword_still_matches():
    """Partial match fallback: 'pembersih wajah' → cleanser."""
    picks = curate([{"kategori": "pembersih wajah lembut", "alasan": "x"}])
    assert picks[0]["nama"] in [p["nama"] for p in CATALOG["cleanser"]]


def test_curate_missing_alasan_key_no_crash():
    picks = curate([{"kategori": "toner"}])
    assert picks


def test_curate_missing_kategori_key_no_crash():
    picks = curate([{"alasan": "x"}])
    assert picks  # falls to default
