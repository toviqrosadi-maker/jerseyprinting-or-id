# Release QA — 10 hero unik artikel Jersey Padel

**PASS — READY FOR REVIEW.** Branch: `feat/jersey-padel-cluster`. Baseline: `4348dd4`. Pemeriksaan: 7 November 2026 (Asia/Jakarta). Belum push, merge, atau deploy.

## Aset dan optimasi

Kesepuluh JPG sumber yang disediakan pengguna dipertahankan byte-nya dan ditambahkan ke version control. Semua sumber berukuran **1376 × 768 px**. WebP utama mengikuti slug halaman dan mempertahankan dimensi tersebut. Tidak ada crop, upscale, generasi, atau perubahan isi visual.

Setiap gambar memiliki dua turunan lebih kecil: **1032 × 576** dan **688 × 384**. Semua rasio tepat 43:24 sehingga pergantian kandidat responsif tidak mengubah tinggi layout. Encoder WebP Chromium memakai kualitas 0,95. Nama turunan: `<slug>-1032.webp` dan `<slug>-688.webp`.

| WebP utama | Byte 1376px | Byte 1032px | Byte 688px |
| --- | ---: | ---: | ---: |
| `bahan-jersey-padel.webp` | 281,470 | 143,656 | 67,140 |
| `desain-jersey-padel-custom.webp` | 303,746 | 176,732 | 97,530 |
| `ukuran-jersey-padel-pria-wanita.webp` | 267,616 | 151,656 | 82,810 |
| `jersey-padel-full-printing-sublimasi.webp` | 375,166 | 208,780 | 113,160 |
| `jersey-padel-komunitas.webp` | 462,862 | 258,848 | 130,466 |
| `jersey-padel-turnamen.webp` | 263,152 | 147,916 | 82,454 |
| `jersey-padel-lengan-panjang-pendek.webp` | 365,660 | 214,120 | 114,572 |
| `jersey-padel-nama-logo-sponsor.webp` | 233,952 | 125,664 | 65,812 |
| `cara-merawat-jersey-padel.webp` | 296,106 | 155,794 | 77,238 |
| `checklist-pesan-jersey-padel-custom.webp` | 345,364 | 183,616 | 88,264 |

Pemetaan lengkap sumber → halaman, dimensi, ukuran file, dan SHA-256: [conversion.json](conversion.json). Penomoran sumber 03–12 mengikuti tabel pengguna, tanpa pertukaran gambar antarartikel.

## Perubahan HTML yang dibatasi

Hanya satu tag `<img>` hero per artikel pendukung yang berubah: `src`, `srcset`, `sizes`, alt yang sesuai isi visual, dimensi 1376 × 768, `loading="eager"`, `fetchpriority="high"`, dan `decoding="async"`.

`sizes` mengikuti grid yang ada: mobile memakai lebar container, desktop memakai kolom kanan. Chromium memilih **688px pada DPR 1** dan **1032px pada DPR 2** untuk seluruh 10 artikel di kedua viewport. File utama 1376px menjadi fallback dan kandidat untuk kebutuhan yang lebih besar. `object-fit: contain` dan rasio asli dipertahankan; sumber tidak dipotong ulang.

Paragraf, heading, caption, header/footer, navigasi, seluruh href, title, meta description, Open Graph, JSON-LD, canonical, dan sitemap tetap. Sesuai instruksi, metadata gambar Open Graph juga tidak diganti. HTML pilar `jersey-padel-custom.html` tetap identik dengan baseline; hero dan banner pilar sebelumnya dipertahankan.

## Masalah CLS yang ditemukan dan diperbaiki

Uji dengan gambar ditunda 120ms menemukan layout shift sebelum gambar selesai decode. Aturan lama `aspect-ratio: auto` menghilangkan reservasi rasio yang diperlukan. Pada pengukuran awal, nilai maksimum 0,04146; temuan juga muncul pada pilar yang sudah ada.

Perbaikan hanya pada `assets/css/padel.css`: tetapkan `aspect-ratio: 1376 / 768` untuk hero cluster dan banner CTA yang mempunyai dimensi tersebut. CSS global tidak berubah. Tampilan setelah gambar dimuat tetap sama; ruang gambar kini disediakan sejak awal. [Bukti sebelum](layout/release-results-before-cls.json) dan [hasil setelah](layout/release-results.json).

**Hasil akhir: CLS 0 pada seluruh 44 kasus**, termasuk saat gambar sengaja diperlambat. Ini pengukuran lab lokal pada konfigurasi yang diuji, bukan klaim data lapangan seluruh pengunjung.

## QA yang dijalankan

Chromium melalui Playwright yang sudah terpasang; tidak ada instalasi paket baru. Matriks lengkap **11 halaman × viewport 1440 × 1000 / 390 × 844 × DPR 1/2**.

| Skrip / pemeriksaan | Hasil |
| --- | --- |
| `qa_padel_support_release.py` | PASS, 44 kasus, CLS maksimum 0, tidak ada crop/stretch atau overflow, seluruh sumber cukup untuk DPR yang diuji |
| `qa_padel.py` | PASS, 1.338 referensi lokal tanpa broken link/aset; title, canonical, H1 dan metadata lolos |
| `qa_padel_browser.py` | PASS, 10 kasus browser dan 44 pemeriksaan anchor; navigasi, FAQ, WhatsApp, dan card Padel berfungsi |
| `qa_padel_images.py` | PASS, 44 kasus seluruh cluster dan decode inventori aset |
| `qa_padel_pillar_assets.py` | PASS, 4 kasus hero/banner pilar dan klik CTA WhatsApp yang diintersepsi lokal |
| Regresi terhadap `4348dd4` | PASS, seluruh HTML identik setelah satu tag hero yang diizinkan dipulihkan; hanya aturan reservasi rasio ditambahkan pada CSS padel |
| Link homepage | PASS, 11/11 halaman tetap memiliki anchor tepat `jersey printing` di isi utama |
| Link pilar | PASS, 10/10 artikel tetap menautkan pilar; pilar tetap menautkan seluruh artikel |
| Keunikan visual | PASS, 10 topik memakai 10 sumber unik yang sudah diperiksa secara visual |
| Integritas sumber | PASS, hash JPG sesuai manifest konversi; dimensi varian tidak melebihi sumber |
| `git diff --check` | PASS |

Skrip QA lama disesuaikan seperlunya: pemeriksaan piksel membaca dimensi file `currentSrc` yang sebenarnya (bukan `naturalWidth` density-corrected dari `srcset`); audit mengaktifkan gambar lazy saat memeriksa decode seluruh aset; regresi historis mengizinkan tepat perubahan tag hero artikel yang baru diotorisasi. Pemeriksaan lain tetap dijalankan. Log dan exit code: [suite-results.json](suite/suite-results.json).

## Screenshot seluruh artikel

Screenshot desktop/mobile diambil pada DPR 1. Kolom DPR 2 menunjukkan bidang hero penuh pada mobile. Rasio dan pemilihan file desktop DPR 2 juga tercatat pada JSON untuk seluruh artikel.

| Halaman | Desktop | Mobile | Bidang hero mobile |
| --- | --- | --- | --- |
| `bahan-jersey-padel.html` | [1440px](layout/bahan-jersey-padel-1440-hero.jpg) | [390px](layout/bahan-jersey-padel-390-hero.jpg) | [DPR 2](layout/bahan-jersey-padel-390-dpr2-image.png) |
| `desain-jersey-padel-custom.html` | [1440px](layout/desain-jersey-padel-custom-1440-hero.jpg) | [390px](layout/desain-jersey-padel-custom-390-hero.jpg) | [DPR 2](layout/desain-jersey-padel-custom-390-dpr2-image.png) |
| `ukuran-jersey-padel-pria-wanita.html` | [1440px](layout/ukuran-jersey-padel-pria-wanita-1440-hero.jpg) | [390px](layout/ukuran-jersey-padel-pria-wanita-390-hero.jpg) | [DPR 2](layout/ukuran-jersey-padel-pria-wanita-390-dpr2-image.png) |
| `jersey-padel-full-printing-sublimasi.html` | [1440px](layout/jersey-padel-full-printing-sublimasi-1440-hero.jpg) | [390px](layout/jersey-padel-full-printing-sublimasi-390-hero.jpg) | [DPR 2](layout/jersey-padel-full-printing-sublimasi-390-dpr2-image.png) |
| `jersey-padel-komunitas.html` | [1440px](layout/jersey-padel-komunitas-1440-hero.jpg) | [390px](layout/jersey-padel-komunitas-390-hero.jpg) | [DPR 2](layout/jersey-padel-komunitas-390-dpr2-image.png) |
| `jersey-padel-turnamen.html` | [1440px](layout/jersey-padel-turnamen-1440-hero.jpg) | [390px](layout/jersey-padel-turnamen-390-hero.jpg) | [DPR 2](layout/jersey-padel-turnamen-390-dpr2-image.png) |
| `jersey-padel-lengan-panjang-pendek.html` | [1440px](layout/jersey-padel-lengan-panjang-pendek-1440-hero.jpg) | [390px](layout/jersey-padel-lengan-panjang-pendek-390-hero.jpg) | [DPR 2](layout/jersey-padel-lengan-panjang-pendek-390-dpr2-image.png) |
| `jersey-padel-nama-logo-sponsor.html` | [1440px](layout/jersey-padel-nama-logo-sponsor-1440-hero.jpg) | [390px](layout/jersey-padel-nama-logo-sponsor-390-hero.jpg) | [DPR 2](layout/jersey-padel-nama-logo-sponsor-390-dpr2-image.png) |
| `cara-merawat-jersey-padel.html` | [1440px](layout/cara-merawat-jersey-padel-1440-hero.jpg) | [390px](layout/cara-merawat-jersey-padel-390-hero.jpg) | [DPR 2](layout/cara-merawat-jersey-padel-390-dpr2-image.png) |
| `checklist-pesan-jersey-padel-custom.html` | [1440px](layout/checklist-pesan-jersey-padel-custom-1440-hero.jpg) | [390px](layout/checklist-pesan-jersey-padel-custom-390-hero.jpg) | [DPR 2](layout/checklist-pesan-jersey-padel-custom-390-dpr2-image.png) |

Data lengkap: [44 kasus dan CLS](layout/release-results.json), [browser lama](suite/qa_padel_browser/browser-results.json), [anchor](suite/qa_padel_browser/anchor-results.json), [audit gambar](suite/qa_padel_images/image-audit.json), dan [pilar](suite/qa_padel_pillar_assets/pillar-assets-results.json).

## File yang disiapkan untuk commit

- Diubah: 10 HTML artikel pendukung; `assets/css/padel.css`; tiga skrip QA lama (`qa_padel_browser.py`, `qa_padel_images.py`, `qa_padel_pillar_assets.py`).
- Ditambahkan: 10 JPG sumber, 30 WebP (10 utama dan 20 turunan responsif), `prepare_padel_support_assets.py`, `qa_padel_support_release.py`, `run_padel_qa.py`, serta laporan/bukti dalam folder ini.
- Tidak berubah: seluruh isi artikel dan metadata SEO, HTML pilar, homepage, halaman lama, sitemap, robots, CSS global, JavaScript utama, dan konfigurasi Vercel.
- Folder `.vscode/` sudah ada sebagai file pengguna yang belum dilacak; tidak disentuh dan tidak dimasukkan commit.

Mengulang pemeriksaan menggunakan interpreter yang sudah memiliki Playwright:

```powershell
& 'C:/Users/toviq13/AppData/Local/Python/pythoncore-3.14-64/python.exe' scripts/qa_padel_support_release.py --output <folder-layout-baru>
& 'C:/Users/toviq13/AppData/Local/Python/pythoncore-3.14-64/python.exe' scripts/run_padel_qa.py --output <folder-suite-baru>
git diff --check
```

Kedua skrip konversi aset (`prepare_...`) adalah utilitas penyiapan, bukan skrip QA; tidak perlu meregenerasi aset pilar untuk menjalankan pemeriksaan. Tidak ada masalah tersisa pada cakupan QA ini. Release tetap menunggu review; tidak ada publikasi otomatis.
