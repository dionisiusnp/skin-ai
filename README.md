# Skin AI

Konsultan skincare personal: upload foto wajah → Gemini (multimodal) kasih
estimasi kondisi kulit + rekomendasi rutinitas & produk.

## Jalankan Lokal
```bash
git clone <repo-url> skin-ai && cd skin-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # include requirements.txt + pytest

cp .env.example .env
# edit .env, isi GEMINI_API_KEY (dapatkan di https://aistudio.google.com/apikey)

uvicorn app.main:app --reload --port 8080
```
Buka http://localhost:8080

## Jalankan Test
```bash
python -m pytest -q
```
CI (`.github/workflows/test.yml`) otomatis jalankan ini di setiap push/PR.

## Struktur Project
```
skin-ai/
├── app/
│   ├── main.py          # FastAPI app, routing, rate limit, CORS
│   ├── config.py         # Settings (pydantic-settings), validasi env
│   ├── gemini_client.py  # Wrapper panggilan Gemini + parsing JSON
│   └── products.py       # Kurasi produk contoh (nanti: API afiliasi asli)
├── tests/                # pytest - jalan tanpa perlu API key sungguhan
├── templates/index.html  # Halaman upload foto
├── static/               # CSS & JS frontend
├── requirements.txt      # Dependency runtime
├── requirements-dev.txt  # + pytest, httpx untuk testing
├── Dockerfile            # Untuk Cloud Run
├── DEPLOY.md             # Panduan deploy lengkap
├── .github/workflows/test.yml  # CI: test otomatis tiap push
└── .env.example
```

## Deploy ke Google Cloud
Lihat **DEPLOY.md** untuk panduan step-by-step (setup project, API key, Secret
Manager, `gcloud run deploy`).

## Catatan Penting
- Ini MVP untuk demo/showcase, bukan produk medis. Selalu tampilkan
  disclaimer "estimasi kosmetik, bukan diagnosis medis".
- Foto wajah adalah data sensitif — saat ini tidak disimpan ke storage apa
  pun (diproses in-memory lalu dibuang). Kalau nanti menambah fitur
  tracking progres (perlu simpan foto), tambahkan consent eksplisit +
  kebijakan retensi/penghapusan data sebelum fitur itu di-ship.
- Kurasi produk di `app/products.py` masih statis/contoh. Untuk versi
  lanjutan, ganti dengan query ke API afiliasi e-commerce sungguhan.
- Endpoint `/analyze` sudah dibatasi rate limit (`ANALYZE_RATE_LIMIT`, default
  10/menit per IP) dan ukuran upload (`MAX_UPLOAD_BYTES`, default 8MB) — atur
  lewat env var sesuai kebutuhan traffic nyata.

## Roadmap Menuju SaaS
- [ ] Auth user (mis. Firebase Auth) untuk fitur premium/tracking progres.
- [ ] Simpan riwayat analisis per user (Firestore) dengan consent & retensi jelas.
- [ ] Ganti kurasi produk statis dengan API afiliasi e-commerce asli.
- [ ] Observability: structured logging ke Cloud Logging, alerting dasar.
- [ ] CI/CD: lanjutkan dari `.github/workflows/test.yml` ke deploy otomatis
      ke Cloud Run saat merge ke `main` (pakai `google-github-actions/deploy-cloudrun`).
