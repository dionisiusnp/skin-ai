"""
Skin AI - Konsultan Skincare Personal
Backend FastAPI: terima foto wajah, panggil Gemini (multimodal), kembalikan
analisis kondisi kulit + rekomendasi rutinitas/produk.

Jalankan lokal:
    pip install -r requirements.txt
    cp .env.example .env   # isi GEMINI_API_KEY
    uvicorn app.main:app --reload --port 8080

Deploy ke Cloud Run: lihat DEPLOY.md
"""

import logging

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.gemini_client import ALLOWED_CONTENT_TYPES, GeminiError, SkinAnalyzer
from app.products import curate

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("skin_ai")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Skin AI")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

_analyzer: SkinAnalyzer | None = None
if settings.is_gemini_configured:
    _analyzer = SkinAnalyzer(api_key=settings.gemini_api_key, model_name=settings.gemini_model)
else:
    logger.warning("GEMINI_API_KEY belum di-set - endpoint /analyze akan menolak request.")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/healthz")
async def healthz():
    """Health check untuk Cloud Run readiness/liveness probe."""
    return {"status": "ok", "gemini_configured": _analyzer is not None}


@app.post("/analyze")
@limiter.limit(settings.analyze_rate_limit)
async def analyze(request: Request, photo: UploadFile = File(...)):
    if _analyzer is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY belum di-set di server. Lihat DEPLOY.md.",
        )

    if photo.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, detail="Format foto harus JPEG, PNG, atau WEBP."
        )

    image_bytes = await photo.read()

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="File foto kosong.")

    if len(image_bytes) > settings.max_upload_bytes:
        max_mb = settings.max_upload_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=413, detail=f"Ukuran foto melebihi batas {max_mb:.0f} MB."
        )

    logger.info("analyze request: size=%d bytes, type=%s", len(image_bytes), photo.content_type)

    try:
        result = _analyzer.analyze(image_bytes, photo.content_type)
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    result["contoh_produk"] = curate(result.get("rekomendasi_kategori_produk", []))
    return JSONResponse(content=result)
