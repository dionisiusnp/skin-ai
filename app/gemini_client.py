"""Wrapper untuk panggilan Gemini API: prompt, parsing JSON, error handling.

Dipisah dari routing (app/main.py) supaya mudah di-unit-test tanpa perlu
jalankan FastAPI atau panggil API sungguhan.
"""

import json
import logging

from google import genai
from google.genai import types

logger = logging.getLogger("skin_ai.gemini")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Prompt terstruktur: minta Gemini mengembalikan JSON yang bisa langsung
# dirender di frontend, dan secara eksplisit membatasi scope ke "estimasi
# kosmetik" (bukan diagnosis medis) untuk alasan etik & kredibilitas produk.
ANALYSIS_PROMPT = """
Kamu adalah asisten kecantikan (BUKAN dokter atau dermatolog). Analisis foto
wajah berikut secara visual dan berikan estimasi KOSMETIK (bukan diagnosis
medis) dalam format JSON PERSIS seperti skema di bawah ini. Jangan tambahkan
teks lain di luar JSON.

Skema JSON:
{
  "jenis_kulit_estimasi": "kering | berminyak | kombinasi | normal | tidak_terdeteksi",
  "concern_utama": ["maks 3 kata kunci singkat, mis. 'kusam', 'pori besar', 'kemerahan'"],
  "catatan_singkat": "1-2 kalimat ringkasan ramah, bukan klinis",
  "rutinitas_pagi": ["langkah 1", "langkah 2", "langkah 3"],
  "rutinitas_malam": ["langkah 1", "langkah 2", "langkah 3"],
  "rekomendasi_kategori_produk": [
    {"kategori": "mis. 'cleanser lembut'", "alasan": "1 kalimat singkat"}
  ],
  "disclaimer": "Ini estimasi kosmetik berbasis citra, bukan diagnosis medis. Konsultasikan ke dokter kulit untuk kondisi yang signifikan atau persisten."
}

Jika gambar tidak menunjukkan wajah manusia dengan jelas, set
"jenis_kulit_estimasi" menjadi "tidak_terdeteksi" dan jelaskan di
"catatan_singkat".
"""


class GeminiError(RuntimeError):
    """Error saat memanggil Gemini atau mem-parsing responsnya."""


def extract_json(text: str) -> dict:
    """Gemini kadang membungkus JSON dengan ```json ... ``` - bersihkan dulu."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


class SkinAnalyzer:
    """Thin wrapper di sekitar google-genai client supaya mudah di-mock di test."""

    def __init__(self, api_key: str, model_name: str):
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    def analyze(self, image_bytes: bytes, mime_type: str) -> dict:
        if mime_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Mime type tidak didukung: {mime_type}")

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ANALYSIS_PROMPT,
                ],
            )
        except Exception as exc:  # noqa: BLE001 - dibungkus jadi error domain kita
            logger.exception("Gemini API call failed")
            raise GeminiError(f"Gagal memanggil Gemini: {exc}") from exc

        try:
            return extract_json(response.text)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Gemini returned unexpected format: %s", response.text[:300])
            raise GeminiError(
                f"Gemini mengembalikan format tak terduga: {exc}"
            ) from exc
