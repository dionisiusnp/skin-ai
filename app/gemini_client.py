"""Gemini API wrapper: prompt, JSON parsing, error handling."""

import json
import logging

from google import genai
from google.genai import types

logger = logging.getLogger("skin_ai.gemini")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Kategori wajib dipakai Gemini agar selalu match KEYWORD_MAP di products.py.
PRODUCT_CATEGORIES = [
    "cleanser",
    "moisturizer",
    "sunscreen",
    "serum niacinamide",
    "serum vitamin C",
    "serum retinol",
    "toner",
    "exfoliator",
    "face mask",
    "eye cream",
    "lip care",
]

ANALYSIS_PROMPT_PRODUK = f"""
Kamu adalah asisten kecantikan (BUKAN dokter atau dermatolog). Analisis foto
wajah berikut secara visual dan berikan estimasi KOSMETIK (bukan diagnosis
medis) dalam format JSON PERSIS seperti skema di bawah ini. Jangan tambahkan
teks lain di luar JSON.

Skema JSON:
{{
  "jenis_kulit_estimasi": "kering | berminyak | kombinasi | normal | tidak_terdeteksi",
  "concern_utama": ["maks 3 kata kunci singkat, mis. 'kusam', 'pori besar', 'kemerahan'"],
  "catatan_singkat": "1-2 kalimat, nada seperti teman yang ngobrol — bukan konsultan formal",
  "rutinitas_pagi": ["langkah singkat dan praktis"],
  "rutinitas_malam": ["langkah singkat dan praktis"],
  "rekomendasi_kategori_produk": [
    {{"kategori": "WAJIB pilih PERSIS dari daftar di bawah", "alasan": "1 kalimat singkat, conversational"}}
  ],
  "disclaimer": "Bukan diagnosis medis. Kalau ada kondisi yang mengganggu, lebih baik konsultasi ke dokter kulit ya."
}}

Untuk field "kategori" di rekomendasi_kategori_produk, HANYA gunakan nilai-nilai
berikut (salin persis, termasuk spasi dan kapital):
{chr(10).join(f"- {c}" for c in PRODUCT_CATEGORIES)}

Pilih 3-4 kategori yang paling relevan untuk kondisi kulit pada foto.

Jika gambar tidak menunjukkan wajah manusia dengan jelas, set
"jenis_kulit_estimasi" menjadi "tidak_terdeteksi" dan jelaskan di
"catatan_singkat".
"""

ANALYSIS_PROMPT_ALAMI = """
Kamu adalah asisten kecantikan alami (BUKAN dokter atau dermatolog). Analisis
foto wajah berikut secara visual dan berikan estimasi KOSMETIK (bukan diagnosis
medis) beserta rekomendasi perawatan berbasis bahan alami/herbal yang mudah
ditemukan di Indonesia. Format JSON PERSIS seperti skema di bawah. Jangan
tambahkan teks lain di luar JSON.

Skema JSON:
{
  "jenis_kulit_estimasi": "kering | berminyak | kombinasi | normal | tidak_terdeteksi",
  "concern_utama": ["maks 3 kata kunci singkat, mis. 'kusam', 'pori besar', 'kemerahan'"],
  "catatan_singkat": "1-2 kalimat, nada seperti teman yang ngobrol — bukan konsultan formal",
  "rutinitas_pagi": ["langkah singkat dan praktis"],
  "rutinitas_malam": ["langkah singkat dan praktis"],
  "rekomendasi_alami": [
    {
      "bahan": "nama bahan alami (mis. 'Lidah Buaya', 'Kunyit', 'Madu')",
      "manfaat": "1 kalimat manfaat spesifik, conversational",
      "cara_pakai": "cara aplikasi singkat, seperti ngasih tahu teman",
      "frekuensi": "mis. '2-3x seminggu' atau 'setiap hari'"
    }
  ],
  "disclaimer": "Bukan diagnosis medis. Kalau ada kondisi yang mengganggu, lebih baik konsultasi ke dokter kulit ya."
}

Rekomendasikan 3-4 bahan alami yang paling relevan. Prioritaskan bahan yang
mudah ditemukan di pasar tradisional atau supermarket Indonesia (lidah buaya,
kunyit, madu, bengkoang, beras, pepaya, teh hijau, minyak kelapa, dll).

Jika gambar tidak menunjukkan wajah manusia dengan jelas, set
"jenis_kulit_estimasi" menjadi "tidak_terdeteksi" dan jelaskan di
"catatan_singkat".
"""


class GeminiError(RuntimeError):
    pass


def _friendly_gemini_error(exc: Exception) -> str:
    msg = str(exc)
    if "402" in msg or "RESOURCE_EXHAUSTED" in msg:
        return (
            "Kuota API Gemini habis. "
            "Top-up credits di https://aistudio.google.com atau coba lagi besok."
        )
    if "429" in msg or "RATE_LIMIT" in msg:
        return "Terlalu banyak request ke Gemini. Tunggu sebentar lalu coba lagi."
    if "403" in msg or "PERMISSION_DENIED" in msg:
        return "API key Gemini tidak valid atau tidak punya akses. Periksa GEMINI_API_KEY di konfigurasi server."
    if "400" in msg or "INVALID_ARGUMENT" in msg:
        return "Format permintaan tidak valid. Pastikan foto wajah jelas dan berformat JPEG, PNG, atau WEBP."
    if "503" in msg or "UNAVAILABLE" in msg:
        return "Layanan Gemini sedang tidak tersedia. Coba lagi dalam beberapa menit."
    if "500" in msg or "INTERNAL" in msg:
        return "Gemini mengalami error internal. Coba lagi dalam beberapa saat."
    return "Gemini tidak dapat dihubungi saat ini. Periksa koneksi atau coba beberapa saat lagi."


def extract_json(text: str) -> dict:
    """Strip optional ```json``` fence then parse."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


class SkinAnalyzer:

    def __init__(self, api_key: str, model_name: str):
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    def analyze(self, image_bytes: bytes, mime_type: str, mode: str = "produk") -> dict:
        if mime_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Mime type tidak didukung: {mime_type}")

        prompt = ANALYSIS_PROMPT_ALAMI if mode == "alami" else ANALYSIS_PROMPT_PRODUK

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
            )
        except Exception as exc:  # noqa: BLE001 - dibungkus jadi error domain kita
            logger.exception("Gemini API call failed")
            raise GeminiError(_friendly_gemini_error(exc)) from exc

        try:
            return extract_json(response.text)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Gemini returned unexpected format: %s", response.text[:300])
            raise GeminiError(
                f"Gemini mengembalikan format tak terduga: {exc}"
            ) from exc
