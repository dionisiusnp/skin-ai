import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FAKE_JPEG = b"\xff\xd8\xff" + b"\x00" * 100  # minimal JPEG magic bytes


# ── /status ──────────────────────────────────────────────────────────────────

def test_status_ok():
    res = client.get("/status")
    assert res.status_code == 200
    assert "gemini_configured" in res.json()


# ── / ────────────────────────────────────────────────────────────────────────

def test_homepage_loads():
    res = client.get("/")
    assert res.status_code == 200


# ── /analyze — validation (no API key needed) ────────────────────────────────

def test_analyze_no_api_key_returns_500():
    """Analyzer None (no API key configured) → 500."""
    with patch("app.main._analyzer", None):
        res = client.post(
            "/analyze",
            files={"photo": ("face.jpg", io.BytesIO(FAKE_JPEG), "image/jpeg")},
        )
    assert res.status_code == 500
    assert "GEMINI_API_KEY" in res.json()["detail"]


def test_analyze_rejects_wrong_content_type():
    """Bad mime type → 400 when analyzer is configured."""
    mock_analyzer = MagicMock()
    with patch("app.main._analyzer", mock_analyzer):
        res = client.post(
            "/analyze",
            files={"photo": ("doc.txt", io.BytesIO(b"text"), "text/plain")},
        )
    assert res.status_code == 400
    assert "JPEG" in res.json()["detail"] or "PNG" in res.json()["detail"]


def test_analyze_rejects_empty_file():
    """Empty file → 400 when analyzer is configured."""
    mock_analyzer = MagicMock()
    with patch("app.main._analyzer", mock_analyzer):
        res = client.post(
            "/analyze",
            files={"photo": ("empty.jpg", io.BytesIO(b""), "image/jpeg")},
        )
    assert res.status_code == 400
    assert "kosong" in res.json()["detail"]


def test_analyze_rejects_oversized_file():
    """File > max_upload_bytes → 413."""
    from app.config import get_settings
    limit = get_settings().max_upload_bytes
    big = io.BytesIO(b"\xff\xd8\xff" + b"x" * (limit + 1))
    mock_analyzer = MagicMock()
    with patch("app.main._analyzer", mock_analyzer):
        res = client.post(
            "/analyze",
            files={"photo": ("big.jpg", big, "image/jpeg")},
        )
    assert res.status_code == 413


# ── /analyze — happy path (Gemini mocked) ────────────────────────────────────

MOCK_PRODUK_RESULT = {
    "jenis_kulit_estimasi": "kombinasi",
    "concern_utama": ["kusam"],
    "catatan_singkat": "Kulit kombinasi ringan.",
    "rutinitas_pagi": ["Cleanser", "Sunscreen"],
    "rutinitas_malam": ["Cleanser", "Moisturizer"],
    "rekomendasi_kategori_produk": [{"kategori": "cleanser", "alasan": "cocok"}],
    "disclaimer": "Bukan diagnosis medis.",
}

MOCK_ALAMI_RESULT = {
    "jenis_kulit_estimasi": "berminyak",
    "concern_utama": ["pori besar"],
    "catatan_singkat": "Kulit cenderung berminyak.",
    "rutinitas_pagi": ["Cuci muka"],
    "rutinitas_malam": ["Masker tanah liat"],
    "rekomendasi_alami": [
        {"bahan": "Lidah Buaya", "manfaat": "Melembapkan", "cara_pakai": "Oleskan gel.", "frekuensi": "Setiap hari"}
    ],
    "disclaimer": "Bukan diagnosis medis.",
}


def test_analyze_produk_mode_returns_contoh_produk():
    mock_analyzer = MagicMock()
    mock_analyzer.analyze.return_value = dict(MOCK_PRODUK_RESULT)
    with patch("app.main._analyzer", mock_analyzer):
        res = client.post(
            "/analyze",
            files={"photo": ("face.jpg", io.BytesIO(FAKE_JPEG), "image/jpeg")},
            data={"rec_mode": "produk"},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["rec_mode"] == "produk"
    assert "contoh_produk" in body
    assert isinstance(body["contoh_produk"], list)


def test_analyze_alami_mode_no_contoh_produk():
    mock_analyzer = MagicMock()
    mock_analyzer.analyze.return_value = dict(MOCK_ALAMI_RESULT)
    with patch("app.main._analyzer", mock_analyzer):
        res = client.post(
            "/analyze",
            files={"photo": ("face.jpg", io.BytesIO(FAKE_JPEG), "image/jpeg")},
            data={"rec_mode": "alami"},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["rec_mode"] == "alami"
    assert "contoh_produk" not in body
    assert "rekomendasi_alami" in body


def test_analyze_invalid_rec_mode_falls_back_to_produk():
    """Unknown rec_mode value → treated as produk."""
    mock_analyzer = MagicMock()
    mock_analyzer.analyze.return_value = dict(MOCK_PRODUK_RESULT)
    with patch("app.main._analyzer", mock_analyzer):
        res = client.post(
            "/analyze",
            files={"photo": ("face.jpg", io.BytesIO(FAKE_JPEG), "image/jpeg")},
            data={"rec_mode": "invalid_mode"},
        )
    assert res.status_code == 200
    assert res.json()["rec_mode"] == "produk"


def test_analyze_gemini_error_returns_502():
    from app.gemini_client import GeminiError
    mock_analyzer = MagicMock()
    mock_analyzer.analyze.side_effect = GeminiError("Kuota habis")
    with patch("app.main._analyzer", mock_analyzer):
        res = client.post(
            "/analyze",
            files={"photo": ("face.jpg", io.BytesIO(FAKE_JPEG), "image/jpeg")},
        )
    assert res.status_code == 502
    assert "Kuota habis" in res.json()["detail"]
