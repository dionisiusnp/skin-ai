import json

import pytest

from app.gemini_client import extract_json


def test_extract_json_plain():
    raw = '{"jenis_kulit_estimasi": "kering"}'
    assert extract_json(raw) == {"jenis_kulit_estimasi": "kering"}


def test_extract_json_with_code_fence():
    raw = '```json\n{"jenis_kulit_estimasi": "berminyak"}\n```'
    assert extract_json(raw) == {"jenis_kulit_estimasi": "berminyak"}


def test_extract_json_with_bare_fence_no_lang():
    raw = '```\n{"a": 1}\n```'
    assert extract_json(raw) == {"a": 1}


def test_extract_json_invalid_raises():
    with pytest.raises(json.JSONDecodeError):
        extract_json("bukan json sama sekali")
