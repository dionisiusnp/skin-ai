import json
from unittest.mock import MagicMock, patch

import pytest

from app.gemini_client import (
    GeminiError,
    SkinAnalyzer,
    _friendly_gemini_error,
    extract_json,
)


# ── extract_json ──────────────────────────────────────────────────────────────

def test_extract_json_plain():
    assert extract_json('{"jenis_kulit_estimasi": "kering"}') == {"jenis_kulit_estimasi": "kering"}


def test_extract_json_with_code_fence():
    raw = '```json\n{"jenis_kulit_estimasi": "berminyak"}\n```'
    assert extract_json(raw) == {"jenis_kulit_estimasi": "berminyak"}


def test_extract_json_with_bare_fence():
    assert extract_json('```\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_with_leading_trailing_whitespace():
    assert extract_json('  {"x": 2}  ') == {"x": 2}


def test_extract_json_invalid_raises():
    with pytest.raises(json.JSONDecodeError):
        extract_json("bukan json sama sekali")


def test_extract_json_empty_string_raises():
    with pytest.raises((json.JSONDecodeError, ValueError)):
        extract_json("")


# ── _friendly_gemini_error ────────────────────────────────────────────────────

@pytest.mark.parametrize("snippet,expected_fragment", [
    ("402 RESOURCE_EXHAUSTED", "Kuota API Gemini habis"),
    ("RESOURCE_EXHAUSTED details", "Kuota API Gemini habis"),
    ("429 Too Many Requests", "Terlalu banyak request"),
    ("403 PERMISSION_DENIED", "API key Gemini tidak valid"),
    ("400 INVALID_ARGUMENT", "Format permintaan tidak valid"),
    ("503 UNAVAILABLE", "sedang tidak tersedia"),
    ("500 INTERNAL server error", "error internal"),
    ("unknown network error", "tidak dapat dihubungi"),
])
def test_friendly_gemini_error_mapping(snippet, expected_fragment):
    exc = Exception(snippet)
    msg = _friendly_gemini_error(exc)
    assert expected_fragment in msg


# ── SkinAnalyzer ──────────────────────────────────────────────────────────────

VALID_RESPONSE = {
    "jenis_kulit_estimasi": "normal",
    "concern_utama": ["kusam"],
    "catatan_singkat": "Kulit terlihat sehat.",
    "rutinitas_pagi": ["Cleanser", "Sunscreen"],
    "rutinitas_malam": ["Cleanser", "Moisturizer"],
    "rekomendasi_kategori_produk": [{"kategori": "cleanser", "alasan": "cocok"}],
    "disclaimer": "Bukan diagnosis medis.",
}


def _make_analyzer() -> SkinAnalyzer:
    with patch("app.gemini_client.genai.Client"):
        return SkinAnalyzer(api_key="fake-key", model_name="gemini-test")


def test_analyzer_rejects_invalid_mime():
    analyzer = _make_analyzer()
    with pytest.raises(ValueError, match="Mime type tidak didukung"):
        analyzer.analyze(b"data", "image/gif")


def test_analyzer_happy_path_produk():
    analyzer = _make_analyzer()
    mock_response = MagicMock()
    mock_response.text = json.dumps(VALID_RESPONSE)
    analyzer._client.models.generate_content.return_value = mock_response

    result = analyzer.analyze(b"\xff\xd8\xff", "image/jpeg", mode="produk")
    assert result["jenis_kulit_estimasi"] == "normal"
    analyzer._client.models.generate_content.assert_called_once()


def test_analyzer_happy_path_alami():
    analyzer = _make_analyzer()
    alami_response = {**VALID_RESPONSE, "rekomendasi_alami": [{"bahan": "Madu"}]}
    mock_response = MagicMock()
    mock_response.text = json.dumps(alami_response)
    analyzer._client.models.generate_content.return_value = mock_response

    result = analyzer.analyze(b"\xff\xd8\xff", "image/jpeg", mode="alami")
    assert "rekomendasi_alami" in result


def test_analyzer_uses_different_prompt_per_mode():
    """Produk and alami modes call generate_content with different prompts."""
    analyzer = _make_analyzer()
    mock_response = MagicMock()
    mock_response.text = json.dumps(VALID_RESPONSE)
    analyzer._client.models.generate_content.return_value = mock_response

    analyzer.analyze(b"\xff\xd8\xff", "image/jpeg", mode="produk")
    produk_call_args = analyzer._client.models.generate_content.call_args

    analyzer.analyze(b"\xff\xd8\xff", "image/jpeg", mode="alami")
    alami_call_args = analyzer._client.models.generate_content.call_args

    assert produk_call_args != alami_call_args


def test_analyzer_gemini_api_exception_raises_gemini_error():
    analyzer = _make_analyzer()
    analyzer._client.models.generate_content.side_effect = RuntimeError("503 UNAVAILABLE")

    with pytest.raises(GeminiError, match="sedang tidak tersedia"):
        analyzer.analyze(b"\xff\xd8\xff", "image/jpeg")


def test_analyzer_bad_json_response_raises_gemini_error():
    analyzer = _make_analyzer()
    mock_response = MagicMock()
    mock_response.text = "ini bukan JSON"
    analyzer._client.models.generate_content.return_value = mock_response

    with pytest.raises(GeminiError):
        analyzer.analyze(b"\xff\xd8\xff", "image/jpeg")
