from app.products import curate


def test_curate_matches_known_category():
    categories = [{"kategori": "cleanser lembut", "alasan": "kulit sensitif"}]
    picks = curate(categories)
    assert picks[0]["untuk"] == "cleanser lembut"
    assert "Facial Wash" in picks[0]["nama"]


def test_curate_unknown_category_falls_back_to_default():
    categories = [{"kategori": "obat ajaib entah apa", "alasan": "x"}]
    picks = curate(categories)
    assert picks  # tidak boleh kosong, harus ada default pick


def test_curate_empty_input_returns_default():
    assert curate([]) != []
