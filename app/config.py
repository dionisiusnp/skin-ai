"""Konfigurasi aplikasi, divalidasi sekali saat startup lewat pydantic-settings.

Semua nilai diambil dari environment variable. Di Cloud Run, GEMINI_API_KEY
di-inject lewat Secret Manager (lihat DEPLOY.md) - jangan commit API key ke
repo mana pun.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Batas ukuran upload foto (bytes). Default 8 MB - cukup untuk foto HP,
    # cegah biaya Gemini membengkak dari upload yang tidak wajar.
    max_upload_bytes: int = 8 * 1024 * 1024

    # Rate limit endpoint /analyze per IP (lihat app/main.py).
    analyze_rate_limit: str = "10/minute"

    # Comma-separated origins untuk CORS. "*" untuk dev; di produksi,
    # set ke domain frontend kamu, mis. "https://skinai.app".
    cors_allow_origins: str = "*"

    log_level: str = "INFO"

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
