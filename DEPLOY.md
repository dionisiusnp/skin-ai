# Panduan Deploy Skin AI ke Google Cloud Run

Panduan ini kamu jalankan sendiri di terminal/laptop kamu (atau Cloud Shell),
karena butuh login ke akun Google Cloud kamu sendiri.

## 0. Prasyarat
- Akun Google Cloud dengan billing aktif (Cloud Run punya free tier yang cukup besar, jadi untuk demo/showcase biasanya gratis).
- Kode sudah di-push ke GitHub (repo private atau public, keduanya bisa).
- (Paling gampang) Buka https://console.cloud.google.com → klik ikon **Cloud Shell** di kanan atas — semua tool (gcloud, git, docker) sudah tersedia tanpa install apa pun.

```bash
# Di Cloud Shell:
git clone https://github.com/<username>/<repo>.git skin-ai
cd skin-ai
```

## 1. Setup Project
```bash
# Login (skip kalau pakai Cloud Shell, sudah otomatis login)
gcloud auth login

# Buat project baru (atau pakai yang sudah ada)
gcloud projects create skin-ai-devfest --name="Skin AI DevFest"
gcloud config set project skin-ai-devfest

# Aktifkan billing untuk project ini lewat Console:
# https://console.cloud.google.com/billing/linkedaccount?project=skin-ai-devfest
```

## 2. Aktifkan API yang Diperlukan
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## 3. Dapatkan Gemini API Key
Cara paling cepat untuk demo (tidak perlu setup Vertex AI penuh):
1. Buka https://aistudio.google.com/apikey
2. Klik "Create API Key", pilih project `skin-ai-devfest` (atau project Google Cloud kamu).
3. Copy API key-nya.

> Alternatif lebih "enterprise" (opsional, untuk versi lanjutan): pakai Vertex AI
> dengan service account alih-alih API key statis. Untuk showcase/demo, API key
> dari AI Studio sudah cukup dan lebih cepat disiapkan.

## 4. Simpan API Key dengan Aman (Secret Manager)
Jangan hardcode API key di kode. Simpan di Secret Manager:
```bash
gcloud services enable secretmanager.googleapis.com

echo -n "PASTE_API_KEY_KAMU_DISINI" | gcloud secrets create gemini-api-key --data-file=-

# Beri akses service account Cloud Run ke secret ini
PROJECT_NUMBER=$(gcloud projects describe skin-ai-devfest --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 5. Deploy ke Cloud Run
Dari folder `skin-ai/` (yang berisi `main.py`, `Dockerfile`, dll):
```bash
gcloud run deploy skin-ai \
  --source . \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --set-secrets=GEMINI_API_KEY=gemini-api-key:latest \
  --memory 512Mi
```
- `--source .` → Cloud Build otomatis build Docker image dari Dockerfile, kamu tidak perlu Docker lokal.
- `--region asia-southeast2` → Jakarta, latency paling rendah untuk demo di Indonesia.
- `--allow-unauthenticated` → supaya bisa diakses publik tanpa login (perlu untuk demo).
- `--set-secrets` → inject API key dari Secret Manager sebagai env var `GEMINI_API_KEY`.

Proses ini akan print URL seperti:
```
Service URL: https://skin-ai-xxxxx-as.a.run.app
```
Itu link yang kamu buka untuk demo & share ke siapa saja.

## 6. Verifikasi
```bash
curl https://skin-ai-xxxxx-as.a.run.app/healthz
# harus return: {"status":"ok","gemini_configured":true}
```
Kalau `gemini_configured` masih `false`, cek lagi langkah Secret Manager di atas.

## 7. Update/Redeploy Setelah Ubah Kode
Setiap kali kamu ubah kode, deploy ulang dengan command yang sama di langkah 5 —
Cloud Run otomatis buat revisi baru dan switch traffic tanpa downtime.

## 8. (Opsional) Custom Domain untuk Demo
Kalau mau URL lebih rapi untuk showcase:
```bash
gcloud run domain-mappings create --service skin-ai --domain skinai.yourdomain.com --region asia-southeast2
```

## 9. Estimasi Biaya
Cloud Run free tier: 2 juta request/bulan, 360rb GB-detik memori gratis.
Untuk demo lomba (puluhan-ratusan request), **kemungkinan besar Rp0** selama
masih dalam free tier. Biaya yang mungkin muncul: pemanggilan Gemini API (cek
harga terbaru di https://ai.google.dev/pricing — tier gratis juga tersedia
dengan rate limit tertentu, cukup untuk demo).

## 10. Checklist Sebelum Naik Panggung
- [ ] Buka URL Cloud Run dari HP/laptop venue, pastikan bisa load (koneksi venue kadang lambat).
- [ ] Siapkan foto contoh di galeri HP sebagai fallback kalau kamera live gagal.
- [ ] Test sekali lagi H-1 jam sebelum demo — Cloud Run instance bisa "cold start" kalau lama tidak dipakai (request pertama agak lambat, ini normal, lakukan 1x warm-up request sebelum naik panggung).
- [ ] Siapkan screenshot/video hasil analisis sebagai backup kalau internet venue down total.
