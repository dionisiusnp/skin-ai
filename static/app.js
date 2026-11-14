const form = document.getElementById("analyzeForm");
const photoInput = document.getElementById("photoInput");
const preview = document.getElementById("preview");
const uploadLabel = document.getElementById("uploadLabel");
const submitBtn = document.getElementById("submitBtn");
const resultEl = document.getElementById("result");

photoInput.addEventListener("change", () => {
  const file = photoInput.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  preview.src = url;
  preview.style.display = "block";
  uploadLabel.textContent = file.name;
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = photoInput.files[0];
  if (!file) return;

  submitBtn.disabled = true;
  submitBtn.textContent = "Menganalisis...";
  resultEl.style.display = "block";
  resultEl.innerHTML = '<p class="loading">Gemini sedang menganalisis foto kamu...</p>';

  const fd = new FormData();
  fd.append("photo", file);

  try {
    const res = await fetch("/analyze", { method: "POST", body: fd });
    const data = await res.json();

    if (!res.ok) {
      resultEl.innerHTML = `<div class="error-box">⚠️ ${data.detail || "Terjadi kesalahan."}</div>`;
      return;
    }

    resultEl.innerHTML = renderResult(data);
  } catch (err) {
    resultEl.innerHTML = `<div class="error-box">⚠️ Gagal terhubung ke server: ${err.message}</div>`;
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Analisis Kulitku";
  }
});

function renderResult(data) {
  const concerns = (data.concern_utama || [])
    .map((c) => `<span class="chip">${escapeHtml(c)}</span>`)
    .join("");

  const pagi = (data.rutinitas_pagi || []).map((s) => `<li>${escapeHtml(s)}</li>`).join("");
  const malam = (data.rutinitas_malam || []).map((s) => `<li>${escapeHtml(s)}</li>`).join("");

  const produk = (data.contoh_produk || [])
    .map(
      (p) => `
      <div class="product-item">
        <span>${escapeHtml(p.nama)} <small>(${escapeHtml(p.untuk || "")})</small></span>
        <span class="price">${escapeHtml(p.harga)}</span>
      </div>`
    )
    .join("");

  return `
    <span class="badge">${escapeHtml(data.jenis_kulit_estimasi || "tidak diketahui")}</span>
    <h2>Hasil Analisis</h2>
    <p>${escapeHtml(data.catatan_singkat || "")}</p>
    <div class="chip-row">${concerns}</div>

    <div class="routine-block">
      <h3>☀️ Rutinitas Pagi</h3>
      <ol>${pagi}</ol>
    </div>
    <div class="routine-block">
      <h3>🌙 Rutinitas Malam</h3>
      <ol>${malam}</ol>
    </div>

    <div class="routine-block">
      <h3>🛒 Contoh Produk</h3>
      ${produk}
    </div>

    <div class="disclaimer-box">${escapeHtml(data.disclaimer || "")}</div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
