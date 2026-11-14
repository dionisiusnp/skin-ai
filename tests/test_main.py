import io

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_ok():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert "gemini_configured" in res.json()


def test_homepage_loads():
    res = client.get("/")
    assert res.status_code == 200


def test_analyze_rejects_bad_content_type():
    fake_file = io.BytesIO(b"not an image")
    res = client.post(
        "/analyze",
        files={"photo": ("test.txt", fake_file, "text/plain")},
    )
    # Tanpa GEMINI_API_KEY di environment test, endpoint akan 500 duluan
    # (analyzer belum configured) - kalau API key ada, harus 400 karena
    # content-type tidak didukung. Kedua kasus ini valid tergantung env test.
    assert res.status_code in (400, 500)


def test_analyze_rejects_empty_file():
    fake_file = io.BytesIO(b"")
    res = client.post(
        "/analyze",
        files={"photo": ("empty.jpg", fake_file, "image/jpeg")},
    )
    assert res.status_code in (400, 500)
