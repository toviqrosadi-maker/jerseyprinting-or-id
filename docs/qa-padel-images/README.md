# Audit ketajaman gambar Jersey Padel

Tanggal: 7 November 2026 (Asia/Jakarta). Branch: `feat/jersey-padel-cluster`. Baseline website: `009e941`.

**Layout/loading: PASS. Ketajaman sumber: NEEDS ASSET.** Tidak ditemukan versi resolusi tinggi dari foto hero yang sama. Gambar dipertahankan; tidak dilakukan upscale, penajaman buatan, recompress, atau penggantian dengan foto lain.

## File hero pilar dan ukuran sebelum/sesudah

Halaman `/jersey-padel-custom.html` menggunakan `/assets/images/product-padel-new.webp` pada elemen `.cluster-hero-media img`. Aset yang sama juga dipakai sebagai `og:image` dan hero seluruh 10 artikel pendukung.

| Atribut | Sebelum audit | Sesudah audit |
| --- | --- | --- |
| File | `assets/images/product-padel-new.webp` | Tetap |
| Resolusi file asli | 600 × 520 px | 600 × 520 px |
| Format | WebP | WebP |
| Ukuran file | 39.494 byte / 38,57 KiB | 39.494 byte / 38,57 KiB |
| SHA-256 | `cfde4355beac099e4cb2a8e8f9ddc2b05de2abfab8d5bfcf99b9c6a1a11aa092` | Identik |

Tidak ada aset keluaran baru karena sumber yang lebih baik belum tersedia. Mengonversi ulang WebP kecil ini tidak mengembalikan detail foto yang sudah hilang.

## Ukuran tampil yang diukur di Chromium

Angka berikut adalah ukuran elemen gambar, tanpa border dan caption, bukan ukuran viewport atau atribut HTML.

| Viewport | Ukuran gambar tampil (CSS px) | Kebutuhan piksel pada DPR 2 | Sumber memenuhi DPR 1? | Sumber memenuhi DPR 2? |
| --- | --- | --- | --- | --- |
| 1440 × 1000 | 481,66 × 417,42 | 963,31 × 834,84 | Ya | Tidak |
| 390 × 844 | 356,80 × 309,22 | 713,59 × 618,44 | Ya | Tidak |

Pada DPR 1, gambar tidak diperbesar melampaui dimensi sumber. Namun, kecukupan jumlah piksel tidak menjamin ketajaman: pemeriksaan visual source 600 × 520 memperlihatkan detail yang sudah lunak. Pada DPR 2, keterbatasan resolusi diperparah karena kebutuhan piksel layar melebihi file asli. Ini merupakan diagnosis berbasis inspeksi sumber dan pengukuran browser; parameter kompresi awal file tidak diketahui.

## Pemeriksaan pemilihan gambar oleh browser

- `src` dan `currentSrc` sama-sama `/assets/images/product-padel-new.webp` pada seluruh 44 kasus.
- Tidak ada `srcset`, `sizes`, atau `<picture><source>` yang menurunkan pilihan resolusi.
- Atribut HTML `width="600" height="520"` sesuai rasio sumber.
- CSS efektif: `width: 100%`, `height: auto`, `object-fit: contain`, `filter: none`, `transform: none`, dan `image-rendering: auto`.
- Rasio gambar tetap; tidak ada stretch atau crop tambahan dari CSS pada dua viewport yang diuji.
- Tidak ada endpoint transformasi/optimasi gambar yang menghasilkan thumbnail lain. Browser memuat aset statis yang sama.

Dengan demikian, tidak ada salah pemilihan thumbnail oleh browser yang dapat diperbaiki lewat `srcset` atau `sizes` saat ini. Varian sumber yang lebih besar harus tersedia terlebih dahulu.

## Penelusuran versi resolusi tinggi

Audit mendekode **62 aset sumber** di direktori `assets/`, memeriksa nama, dimensi, ukuran byte, hash, [lembar kontak visual](source-assets-contact-sheet.jpg), serta riwayat Git lokal yang tersedia. Screenshot di direktori dokumentasi tidak diperlakukan sebagai file master.

| Kandidat | Resolusi | Ukuran | Hasil |
| --- | --- | ---: | --- |
| `product-padel-new.webp` | 600 × 520 | 39.494 byte | Foto hero aktif; hanya versi ini yang ditemukan |
| `product-padel.webp` | 639 × 1228 | 66.742 byte | Foto berbeda: pakaian hitam di latar studio; bukan versi asli beresolusi tinggi dari hero aktif |
| Aset komposit jenis jersey | Bidang keseluruhan lebih besar | Tercatat dalam inventori | Berisi beberapa panel/thumbnail; tidak ditemukan foto hero yang sama sebagai master utuh beresolusi lebih tinggi |

Riwayat kedua file padel menunjuk pada commit awal `36c3b54`. Tidak ditemukan revisi master beresolusi lebih tinggi pada riwayat Git lokal. Gambar lain tidak dipakai sebagai pengganti tanpa arahan pemilik situs.

## Audit 10 artikel pendukung

Semua artikel memakai file hero yang sama, 600 × 520 px / 39.494 byte, dengan ukuran tampil sama seperti pilar. Tidak ada gambar inline dalam isi artikel; logo header/footer merupakan komponen bersama yang tetap dipertahankan.

| Artikel | Loading/layout 1440px & 390px | Ketajaman hero DPR 2 |
| --- | --- | --- |
| `bahan-jersey-padel.html` | PASS | Perlu aset lebih tinggi |
| `desain-jersey-padel-custom.html` | PASS | Perlu aset lebih tinggi |
| `ukuran-jersey-padel-pria-wanita.html` | PASS | Perlu aset lebih tinggi |
| `jersey-padel-full-printing-sublimasi.html` | PASS | Perlu aset lebih tinggi |
| `jersey-padel-komunitas.html` | PASS | Perlu aset lebih tinggi |
| `jersey-padel-turnamen.html` | PASS | Perlu aset lebih tinggi |
| `jersey-padel-lengan-panjang-pendek.html` | PASS | Perlu aset lebih tinggi |
| `jersey-padel-nama-logo-sponsor.html` | PASS | Perlu aset lebih tinggi |
| `cara-merawat-jersey-padel.html` | PASS | Perlu aset lebih tinggi |
| `checklist-pesan-jersey-padel-custom.html` | PASS | Perlu aset lebih tinggi |

Temuan ketajaman berlaku bagi seluruh cluster, bukan hanya pilar. Seluruh gambar berhasil dimuat; tidak ada gambar rusak atau overflow horizontal.

## Kebutuhan aset pengganti

Prioritas: **file master foto yang sama**, tajam pada resolusi asli, idealnya **1800 × 1560 px** atau lebih besar dengan rasio 15:13 dan komposisi yang sama. File harus memiliki detail asli, bukan hasil memperbesar 600 × 520. Ukuran tersebut memberi ruang untuk optimasi WebP dan varian responsif tanpa mengubah bidang hero.

Untuk viewport desktop yang diuji, kebutuhan minimum matematis DPR 2 sekitar 964 × 835 px; master yang lebih besar disarankan agar ada ruang optimasi dan kebutuhan responsif. Jika foto yang sama tidak tersedia, diperlukan aset padel baru yang dipilih/disetujui pemilik situs, dengan komposisi yang sesuai. Audit ini tidak memilih atau membuat pengganti.

Setelah master tersedia: optimalkan ke WebP dari sumber asli, verifikasi detail pada DPR 1/2, lalu gunakan varian responsif bila diperlukan sambil mempertahankan rasio dan layout. Jangan menetapkan kualitas kompresi atau ukuran byte akhir sebelum hasil visual diperiksa.

## Hasil QA dan bukti

Playwright menggunakan Chromium `153.0.8010.12` yang sudah tersedia. **44 kasus**: 11 halaman × 2 viewport × DPR 1/2. Semua kasus lulus loading, HTTP 200, satu H1, serta pemeriksaan overflow; tidak ada page error. Pada 22 kasus DPR 2, kebutuhan piksel hero melampaui sumber; temuan ini dicatat terpisah dari kelulusan layout.

`python scripts/qa_padel.py` juga lulus: 1.307 referensi lokal tanpa broken link/aset. `git diff --check` lulus. Seluruh file website yang sudah dilacak tetap identik dengan baseline; penambahan hanya berupa skrip audit dan dokumen/bukti QA. Desain, teks, canonical, sitemap, internal link, serta konfigurasi Vercel tidak berubah.

| Bukti | DPR 1 | DPR 2 |
| --- | --- | --- |
| Hero halaman pada 1440px | [Screenshot](pillar-1440-dpr1-hero.jpg) | [Screenshot](pillar-1440-dpr2-hero.jpg) |
| Detail bidang gambar pada 1440px | [PNG](pillar-1440-dpr1-image.png) | [PNG](pillar-1440-dpr2-image.png) |
| Hero halaman pada 390px | [Screenshot](pillar-390-dpr1-hero.jpg) | [Screenshot](pillar-390-dpr2-hero.jpg) |
| Detail bidang gambar pada 390px | [PNG](pillar-390-dpr1-image.png) | [PNG](pillar-390-dpr2-image.png) |

PNG detail merupakan screenshot render browser pada DPR terkait, bukan file hero baru atau hasil upscale untuk dipakai di website. Data seluruh halaman dan inventori: [image-audit.json](image-audit.json).

Untuk mengulang audit:

```powershell
& 'C:/Users/toviq13/AppData/Local/Python/pythoncore-3.14-64/python.exe' scripts/qa_padel_images.py --output <folder-bukti-baru>
python scripts/qa_padel.py
```

Tidak ada push, merge, atau deploy. Peningkatan ketajaman menunggu aset sumber yang memenuhi kebutuhan.
