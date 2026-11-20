// === State ===
let activeMode = 'camera';
let recMode = 'produk'; // 'produk' | 'alami'
let isDummy = false;
let webcamStream = null;
let capturedBlob = null;
let lastResult = null;
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

// === DOM refs ===
const form           = document.getElementById('analyzeForm');
const btnModeCamera  = document.getElementById('btnModeCamera');
const btnModeGallery = document.getElementById('btnModeGallery');
const btnRecProduk   = document.getElementById('btnRecProduk');
const btnRecAlami    = document.getElementById('btnRecAlami');
const btnDummy       = document.getElementById('btnDummy');
const capturePlaceholder = document.getElementById('capturePlaceholder');
const placeholderIcon    = document.getElementById('placeholderIcon');
const webcamVideo   = document.getElementById('webcamVideo');
const preview       = document.getElementById('preview');
const photoInput    = document.getElementById('photoInput');
const captureInput  = document.getElementById('captureInput');
const snapCanvas    = document.getElementById('snapCanvas');
const startCamBtn   = document.getElementById('startCamBtn');
const snapBtn       = document.getElementById('snapBtn');
const pickFileBtn   = document.getElementById('pickFileBtn');
const retakeBtn     = document.getElementById('retakeBtn');
const submitBtn     = document.getElementById('submitBtn');
const resultEl      = document.getElementById('result');

// === Mode toggle (kamera / galeri) ===
btnModeCamera.addEventListener('click', () => setMode('camera'));
btnModeGallery.addEventListener('click', () => setMode('gallery'));

// === Rec mode toggle (produk / alami) ===
btnRecProduk.addEventListener('click', () => setRecMode('produk'));
btnRecAlami.addEventListener('click',  () => setRecMode('alami'));

// === Dummy toggle ===
btnDummy.addEventListener('click', () => {
  isDummy = !isDummy;
  btnDummy.classList.toggle('active', isDummy);
  btnDummy.textContent = isDummy ? '🎭 Mode demo: ON' : '🎭 Mode demo: OFF';
});

function setRecMode(mode) {
  recMode = mode;
  btnRecProduk.classList.toggle('active', mode === 'produk');
  btnRecAlami.classList.toggle('active',  mode === 'alami');
  btnRecAlami.classList.toggle('alami-active', mode === 'alami');
  btnRecProduk.classList.remove('alami-active');
}

function setMode(mode) {
  activeMode = mode;
  resetCapture();
  btnModeCamera.classList.toggle('active', mode === 'camera');
  btnModeGallery.classList.toggle('active', mode === 'gallery');
  startCamBtn.style.display = mode === 'camera' ? '' : 'none';
  pickFileBtn.style.display = mode === 'gallery' ? '' : 'none';
  snapBtn.style.display = 'none';
  retakeBtn.style.display = 'none';
  placeholderIcon.textContent = mode === 'camera' ? '📷' : '📁';
}

// === Camera flow ===
startCamBtn.addEventListener('click', async () => {
  if (isMobile) {
    captureInput.click();
  } else {
    await startWebcam();
  }
});

async function startWebcam() {
  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
    });
    webcamVideo.srcObject = webcamStream;
    webcamVideo.style.display = 'block';
    capturePlaceholder.style.display = 'none';
    preview.style.display = 'none';
    startCamBtn.style.display = 'none';
    snapBtn.style.display = '';
    retakeBtn.style.display = 'none';
    submitBtn.disabled = true;
    capturedBlob = null;
  } catch {
    alert('Kamera tidak bisa diakses. Coba pilih mode Galeri atau periksa izin kamera browser.');
  }
}

snapBtn.addEventListener('click', () => {
  snapCanvas.width = webcamVideo.videoWidth;
  snapCanvas.height = webcamVideo.videoHeight;
  snapCanvas.getContext('2d').drawImage(webcamVideo, 0, 0);
  stopWebcam();

  const dataUrl = snapCanvas.toDataURL('image/jpeg', 0.9);
  preview.src = dataUrl;
  preview.style.display = 'block';
  capturePlaceholder.style.display = 'none';
  snapBtn.style.display = 'none';
  retakeBtn.style.display = '';
  submitBtn.disabled = false;

  snapCanvas.toBlob(blob => { capturedBlob = blob; }, 'image/jpeg', 0.9);
});

function stopWebcam() {
  if (webcamStream) {
    webcamStream.getTracks().forEach(t => t.stop());
    webcamStream = null;
  }
  webcamVideo.style.display = 'none';
  webcamVideo.srcObject = null;
}

// Mobile: native camera capture
captureInput.addEventListener('change', () => {
  const file = captureInput.files[0];
  if (!file) return;
  showFilePreview(file);
  capturedBlob = null;
});

// === Gallery flow ===
pickFileBtn.addEventListener('click', () => photoInput.click());

photoInput.addEventListener('change', () => {
  const file = photoInput.files[0];
  if (!file) return;
  showFilePreview(file);
  capturedBlob = null;
});

function showFilePreview(file) {
  const url = URL.createObjectURL(file);
  preview.src = url;
  preview.style.display = 'block';
  capturePlaceholder.style.display = 'none';
  retakeBtn.style.display = '';
  submitBtn.disabled = false;
}

// === Retake ===
retakeBtn.addEventListener('click', () => {
  resetCapture();
  if (activeMode === 'camera') startCamBtn.style.display = '';
  else pickFileBtn.style.display = '';
});

function resetCapture() {
  stopWebcam();
  capturedBlob = null;
  preview.src = '';
  preview.style.display = 'none';
  capturePlaceholder.style.display = '';
  submitBtn.disabled = true;
  photoInput.value = '';
  captureInput.value = '';
  snapBtn.style.display = 'none';
  retakeBtn.style.display = 'none';
}

// === Form submit ===
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  let blob = capturedBlob || captureInput.files[0] || photoInput.files[0];
  if (!blob) return;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Menganalisis...';
  resultEl.style.display = 'block';
  resultEl.className = 'card result-card';
  resultEl.innerHTML = skeletonHTML();
  resultEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  if (isDummy) {
    // short delay biar skeleton keliatan
    await new Promise(r => setTimeout(r, 800));
    showResult(buildDemoData(recMode));
    submitBtn.disabled = false;
    submitBtn.textContent = 'Analisis Kulitku';
    return;
  }

  const fd = new FormData();
  fd.append('photo', blob, 'photo.jpg');
  fd.append('rec_mode', recMode);

  try {
    const res  = await fetch('/analyze', { method: 'POST', body: fd });
    const data = await res.json();

    if (!res.ok) {
      resultEl.innerHTML = `<div class="error-box">⚠️ ${escapeHtml(data.detail || 'Terjadi kesalahan.')}</div>`;
      return;
    }

    showResult(data);
  } catch (err) {
    resultEl.innerHTML = `<div class="error-box">⚠️ Gagal terhubung ke server: ${escapeHtml(err.message)}</div>`;
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Analisis Kulitku';
  }
});

function showResult(data) {
  lastResult = data;
  resultEl.className = 'card result-card';
  void resultEl.offsetWidth; // force reflow so animation replays
  resultEl.classList.add('slide-up');
  resultEl.innerHTML = renderResult(data);
  resultEl.querySelector('.share-btn').addEventListener('click', shareResult);
}

// === Skeleton ===
function skeletonHTML() {
  const lines = [100, 88, 65, 0, 40, 72, 58, 80].map(w =>
    w ? `<div class="skel" style="width:${w}%"></div>` : '<div style="height:12px"></div>'
  ).join('');
  return `
    <div class="skeleton-wrap">${lines}</div>
    <p class="loading">Bentar ya, lagi dianalisis…</p>
  `;
}

// === Result render ===
function renderResult(data) {
  const mode = data.rec_mode || 'produk';

  const concerns = (data.concern_utama || [])
    .map(c => `<span class="chip">${escapeHtml(c)}</span>`).join('');

  const pagi  = (data.rutinitas_pagi  || []).map(s => `<li>${escapeHtml(s)}</li>`).join('');
  const malam = (data.rutinitas_malam || []).map(s => `<li>${escapeHtml(s)}</li>`).join('');

  const rekSection = mode === 'alami'
    ? renderAlami(data.rekomendasi_alami || [])
    : renderProduk(data.contoh_produk   || []);

  return `
    <span class="badge">${escapeHtml(data.jenis_kulit_estimasi || 'tidak diketahui')}</span>
    <p class="result-note">${escapeHtml(data.catatan_singkat || '')}</p>
    <div class="chip-row">${concerns}</div>

    <div class="routine-block">
      <h3>☀️ Rutinitas Pagi</h3>
      <ol>${pagi}</ol>
    </div>
    <div class="routine-block">
      <h3>🌙 Rutinitas Malam</h3>
      <ol>${malam}</ol>
    </div>

    ${rekSection}

    <div class="disclaimer-box">${escapeHtml(data.disclaimer || '')}</div>
    <button type="button" class="share-btn">Bagikan ke teman →</button>
  `;
}

function renderProduk(produkList) {
  const items = produkList.map(p => `
    <div class="product-item">
      <div class="product-info">
        <span class="product-name">${escapeHtml(p.nama)}</span>
        <span class="product-meta">${escapeHtml(p.merek || '')} · ${escapeHtml(p.untuk || '')}</span>
        ${p.alasan ? `<span class="product-reason">${escapeHtml(p.alasan)}</span>` : ''}
      </div>
      <div class="product-right">
        <span class="price">${escapeHtml(p.harga)}</span>
        <a class="shopee-link"
           href="https://shopee.co.id/search?keyword=${encodeURIComponent(p.nama)}"
           target="_blank" rel="noopener noreferrer">Cari →</a>
      </div>
    </div>
  `).join('');

  return `
    <div class="routine-block">
      <h3>Yang bisa kamu coba</h3>
      <p class="shopee-note">Harga perkiraan — klik Cari untuk beli di Shopee</p>
      ${items}
    </div>
  `;
}

function renderAlami(bahan) {
  const items = bahan.map(b => `
    <div class="herb-item">
      <div class="herb-header">
        <span class="herb-name">🌿 ${escapeHtml(b.bahan)}</span>
        ${b.frekuensi ? `<span class="herb-freq">${escapeHtml(b.frekuensi)}</span>` : ''}
      </div>
      <span class="herb-benefit">${escapeHtml(b.manfaat)}</span>
      <span class="herb-how"><strong>Cara pakai:</strong> ${escapeHtml(b.cara_pakai)}</span>
    </div>
  `).join('');

  return `
    <div class="routine-block">
      <h3>🌿 Bisa kamu coba di rumah</h3>
      <p class="shopee-note">Semua bahan bisa dicari di pasar atau supermarket dekat rumah.</p>
      ${items}
    </div>
  `;
}

function shareResult() {
  if (!lastResult) return;

  const existing = document.getElementById('sharePanel');
  if (existing) { existing.remove(); return; }

  const text =
    `Kulit ${lastResult.jenis_kulit_estimasi} — ${(lastResult.concern_utama || []).join(', ')}\n\n` +
    `${lastResult.catatan_singkat}\n\n` +
    `Cek kondisi kulitmu juga: https://skin-ai-529211426509.asia-southeast2.run.app`;
  const url  = 'https://skin-ai-529211426509.asia-southeast2.run.app';

  const options = [
    {
      icon: '💬', label: 'WhatsApp',
      href: `https://wa.me/?text=${encodeURIComponent(text)}`,
    },
    {
      icon: '✈️', label: 'Telegram',
      href: `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`,
    },
    {
      icon: '𝕏', label: 'X / Twitter',
      href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`,
    },
  ];

  const panel = document.createElement('div');
  panel.id = 'sharePanel';
  panel.className = 'share-panel';
  panel.innerHTML = options.map(o => `
    <a class="share-option" href="${o.href}" target="_blank" rel="noopener noreferrer">
      <span class="share-option-icon">${o.icon}</span>
      <span class="share-option-label">${o.label}</span>
    </a>
  `).join('') + `
    <button type="button" class="share-option share-copy" id="shareCopyBtn">
      <span class="share-option-icon">📋</span>
      <span class="share-option-label">Salin teks</span>
    </button>
  `;

  const shareBtn = resultEl.querySelector('.share-btn');
  shareBtn.insertAdjacentElement('afterend', panel);

  panel.querySelector('#shareCopyBtn').addEventListener('click', () => {
    navigator.clipboard.writeText(text)
      .then(() => {
        const btn = panel.querySelector('#shareCopyBtn .share-option-label');
        btn.textContent = 'Tersalin! ✓';
        setTimeout(() => { btn.textContent = 'Salin teks'; }, 2000);
      })
      .catch(() => {});
  });

  // tutup panel saat klik di luar
  setTimeout(() => {
    document.addEventListener('click', function handler(e) {
      if (!panel.contains(e.target) && e.target !== shareBtn) {
        panel.remove();
        document.removeEventListener('click', handler);
      }
    });
  }, 0);
}

const DEMO_BASE = {
  jenis_kulit_estimasi: 'kombinasi',
  concern_utama: ['pori besar', 'kusam', 'kemerahan ringan'],
  catatan_singkat: 'Kulitmu kombinasi — daerah hidung dan dahi cenderung lebih berminyak, pipi lebih normal. Ada sedikit kusam yang bisa membaik dengan rutinitas yang rutin.',
  rutinitas_pagi: [
    'Cuci muka dengan cleanser lembut',
    'Toner hydrating untuk hidrasi awal',
    'Serum niacinamide untuk pori & sebum',
    'Moisturizer gel ringan',
    'Sunscreen SPF 50 — wajib setiap hari!',
  ],
  rutinitas_malam: [
    'Double cleanse (oil cleanser + water-based)',
    'Exfoliating toner (BHA) 2–3× seminggu',
    'Serum vitamin C untuk mencerahkan',
    'Moisturizer lebih rich untuk repair malam',
  ],
  disclaimer: 'Bukan diagnosis medis. Kalau ada kondisi yang mengganggu, lebih baik konsultasi ke dokter kulit ya.',
};

function buildDemoData(mode) {
  return mode === 'alami'
    ? {
        ...DEMO_BASE,
        rec_mode: 'alami',
        rekomendasi_alami: [
          {
            bahan: 'Lidah Buaya',
            manfaat: 'Melembapkan dan meredakan kemerahan pada kulit kombinasi',
            cara_pakai: 'Oleskan gel segar langsung ke wajah selama 15–20 menit, lalu bilas dengan air dingin.',
            frekuensi: 'Setiap hari',
          },
          {
            bahan: 'Madu Murni',
            manfaat: 'Antibakteri alami, membantu mengurangi kusam dan melembapkan',
            cara_pakai: 'Aplikasikan tipis sebagai masker selama 10 menit sebelum mandi.',
            frekuensi: '3× seminggu',
          },
          {
            bahan: 'Air Beras (Fermented Rice Water)',
            manfaat: 'Mencerahkan dan mengecilkan tampilan pori secara alami',
            cara_pakai: 'Gunakan sebagai toner — usapkan dengan kapas setelah cuci muka.',
            frekuensi: 'Setiap hari (pagi)',
          },
          {
            bahan: 'Kunyit + Madu',
            manfaat: 'Anti-inflamasi untuk meredakan kemerahan dan meratakan warna kulit',
            cara_pakai: 'Campur ½ sdt kunyit bubuk + 1 sdt madu, oleskan 10 menit lalu bilas.',
            frekuensi: '2× seminggu (malam)',
          },
        ],
      }
    : {
        ...DEMO_BASE,
        rec_mode: 'produk',
        contoh_produk: [
          {
            nama: 'Somethinc Low pH Cleanser', merek: 'Somethinc',
            harga: 'Rp 55.000 – 75.000', untuk: 'cleanser lembut',
            alasan: 'Membersihkan tanpa merusak skin barrier',
          },
          {
            nama: 'Skintific 10% Niacinamide Serum', merek: 'Skintific',
            harga: 'Rp 55.000 – 80.000', untuk: 'serum niacinamide',
            alasan: 'Mengecilkan pori dan mengontrol minyak di T-zone',
          },
          {
            nama: 'Azarine Hydrasoothe Sunscreen SPF 45', merek: 'Azarine',
            harga: 'Rp 45.000 – 65.000', untuk: 'sunscreen SPF50',
            alasan: 'Proteksi UV harian ringan, tidak lengket',
          },
          {
            nama: 'Somethinc BHA Pore Cleansing Toner', merek: 'Somethinc',
            harga: 'Rp 55.000 – 80.000', untuk: 'toner BHA',
            alasan: 'Eksfoliasi lembut untuk membuka pori tersumbat',
          },
        ],
      };
}

// === Helpers ===
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}
