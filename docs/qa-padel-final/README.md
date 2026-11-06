# FINAL QA — Jersey Padel Custom v4.7

**PASS — READY FOR REVIEW** setelah satu perbaikan navigasi anchor.

Tanggal: 7 November 2026, Asia/Jakarta. Commit yang direview: `c3d19b3`. Branch: `feat/jersey-padel-cluster`. Tidak ada push, merge, atau deploy.

## Lingkungan dan cakupan

Playwright tersedia pada interpreter `C:/Users/toviq13/AppData/Local/Python/pythoncore-3.14-64/python.exe`, meskipun tidak tersedia pada interpreter Python default. Chromium headless yang sudah terpasang berhasil dijalankan: `153.0.8010.12`. Tidak dilakukan instalasi paket atau browser baru.

Lima halaman diuji dengan browser pada viewport **1440 × 1000** dan **390 × 844**, skala perangkat 1:

- `/jersey-padel-custom.html`
- `/bahan-jersey-padel.html`
- `/desain-jersey-padel-custom.html`
- `/checklist-pesan-jersey-padel-custom.html`
- `/index.html` (homepage lokal)

Total 10 kasus browser lengkap. Uji regresi tambahan mencakup tombol ke `#panduan` dan tautan pertama daftar isi pada **seluruh 11 halaman × 2 viewport**, total 44 kasus anchor. Server menggunakan port localhost sementara dan dimatikan otomatis setelah pengujian.

## Hasil PASS/FAIL

| Pemeriksaan | Hasil | Bukti/catatan |
| --- | --- | --- |
| Browser tersedia | PASS | Playwright dan Chromium berhasil dijalankan |
| Lima halaman, dua viewport | PASS | 10/10 kasus lengkap, HTTP 200, tidak ada exception atau page error |
| Hero dan gambar halaman | PASS | Seluruh gambar memiliki natural dimensions, selesai dimuat, dan tidak ada gambar rusak; screenshot ditinjau |
| Gambar dalam isi artikel | N/A | Artikel baru tidak memuat gambar inline; hero memakai aset padel yang sudah tersedia dan relevan |
| Heading dan paragraf | PASS | Tidak ada heading overflow/clipped; paragraf sampel 16px dengan line-height 27,2px; visual ditinjau |
| Navigasi desktop/mobile | PASS | Navigasi desktop tampil; tombol mobile membuka menu dan menu tertutup setelah navigasi ke Jenis Jersey |
| WhatsApp | PASS | Semua href menuju `6281221111398`; klik CTA membuka popup yang diintersepsi lokal, tanpa pesan atau request nyata ke WhatsApp |
| FAQ pilar | PASS | Disclosure bisa dibuka pada desktop dan mobile |
| Overflow horizontal | PASS | Lebar dokumen tidak melebihi viewport pada 10 kasus |
| Card Jersey Padel | PASS | Href persis `/jersey-padel-custom.html`; klik card menuju pilar pada kedua viewport |
| Link kontekstual sampel | PASS | Tujuan lokal merespons 200; klik link artikel benar-benar menuju halaman yang dimaksud |
| Anchor di bawah sticky header | FAIL → PASS | Masalah ditemukan sebelum perbaikan; 44/44 pemeriksaan ulang lulus setelah perbaikan |
| Link lokal/aset seluruh situs | PASS | 1.307 referensi diperiksa, tanpa path/aset/fragment rusak |
| Canonical, title, H1, meta, sitemap | PASS | Skrip QA statis lulus; tidak ada perubahan canonical, URL, atau sitemap dalam tahap FINAL QA |
| Link pendukung → pilar | PASS | 10/10 artikel memiliki link pilar secara kontekstual; pilar menautkan seluruh artikel |
| Link homepage | PASS | 11/11 halaman memiliki link `/` dengan anchor tepat `jersey printing` dalam paragraf yang relevan |
| Regresi konten dan halaman lama | PASS | Perbandingan ke `c3d19b3`: isi 11 halaman tetap, hanya link stylesheet khusus ditambahkan; homepage dan empat halaman lama tetap |
| Kebersihan diff | PASS | `git diff --check` lulus |

## Masalah yang ditemukan dan diperbaiki

**Heading tertutup sticky header setelah klik daftar isi.** Sebelum perbaikan, heading berhenti di sekitar posisi y=0, sementara header menutup area hingga y=77px. Masalah terkonfirmasi pada pilar dan ketiga artikel sampel di kedua viewport.

Perbaikan terbatas:

- Menambahkan `assets/css/padel.css` dengan `scroll-margin-top: 96px` untuk `.article-wrap[id]` dan `.article [id]`.
- Memuat stylesheet tersebut hanya pada 11 halaman padel.
- Menambahkan `scripts/qa_padel_browser.py` untuk mengulangi pemeriksaan browser dan regresi anchor.

Setelah perbaikan, posisi tujuan anchor berada pada y=95,56–96,39px, di bawah header 77px. Tidak ada perubahan isi, urutan heading, URL, canonical, sitemap, halaman lama, stylesheet global, JavaScript utama, atau gambar. Bukti sebelum dan sesudah:

| Viewport | Sebelum | Sesudah |
| --- | --- | --- |
| 1440px | [FAIL: heading tertutup](pillar-1440-anchor-before.png) | [PASS: heading terlihat](pillar-1440-anchor-after.jpg) |
| 390px | [FAIL: heading tertutup](pillar-390-anchor-before.png) | [PASS: heading terlihat](pillar-390-anchor-after.jpg) |

## Audit editorial 11 halaman

| Halaman | Intent/sudut pembahasan | Status |
| --- | --- | --- |
| Pilar | Produk, pertimbangan spesifikasi, pemesanan, FAQ dan konsultasi | PASS |
| Bahan | Penilaian sampel dan kenyamanan kain | PASS |
| Desain | Brief visual, warna, komposisi dan mockup | PASS |
| Ukuran | Metode ukur, pola, kelonggaran dan daftar ukuran tim | PASS |
| Sublimasi | File, kecocokan bahan, warna dan sambungan panel | PASS |
| Komunitas | Pengambilan keputusan kelompok dan administrasi anggota | PASS |
| Turnamen | Ketentuan acara, tenggat, penggantian peserta dan distribusi | PASS |
| Lengan | Penutupan, ruang gerak, lapisan dalam dan variasi model | PASS |
| Nama/logo/sponsor | Kualitas aset, ejaan, persetujuan dan hierarki penempatan | PASS |
| Perawatan | Rutinitas setelah bermain sampai pencucian dan penyimpanan | PASS |
| Checklist | Titik verifikasi brief, penawaran, persetujuan dan penerimaan | PASS |

Tidak ditemukan paragraf identik minimal 25 kata, pasangan paragraf lintas halaman dengan kemiripan urutan kata ≥65%, atau subheading duplikat. Subheading menjelaskan keputusan spesifik dalam topiknya; tidak ditemukan pola judul generik berulang yang memerlukan perbaikan. Tumpang tindih terbatas mengenai bahan, ukuran, dan persetujuan relevan dengan konteks masing-masing artikel.

Frasa persis `jersey padel custom` muncul 7 kali pada isi pilar dan 1–3 kali pada isi setiap artikel pendukung (heading dalam article ikut dihitung). Pemeriksaan konteks tidak menemukan keyword stuffing. Setiap halaman mempunyai satu tautan homepage dengan anchor `jersey printing`; paragraf menghubungkannya dengan layanan umum, sedangkan materi utama tetap membahas padel. Tidak dilakukan penulisan ulang editorial.

Kemiripan pasangan halaman tertinggi berdasarkan Jaccard urutan lima kata tetap 0,265%. Angka ini adalah alat pemeriksaan pengulangan internal, bukan penilaian plagiarisme eksternal atau jaminan mesin pencari.

## Screenshot halaman

| Halaman | Hero 1440px | Hero 390px | Isi 1440px | Isi 390px |
| --- | --- | --- | --- | --- |
| Pilar | [Lihat](jersey-padel-custom-1440-hero.jpg) | [Lihat](jersey-padel-custom-390-hero.jpg) | [Lihat](jersey-padel-custom-1440-article.jpg) | [Lihat](jersey-padel-custom-390-article.jpg) |
| Bahan | [Lihat](bahan-jersey-padel-1440-hero.jpg) | [Lihat](bahan-jersey-padel-390-hero.jpg) | [Lihat](bahan-jersey-padel-1440-article.jpg) | [Lihat](bahan-jersey-padel-390-article.jpg) |
| Desain | [Lihat](desain-jersey-padel-custom-1440-hero.jpg) | [Lihat](desain-jersey-padel-custom-390-hero.jpg) | [Lihat](desain-jersey-padel-custom-1440-article.jpg) | [Lihat](desain-jersey-padel-custom-390-article.jpg) |
| Checklist | [Lihat](checklist-pesan-jersey-padel-custom-1440-hero.jpg) | [Lihat](checklist-pesan-jersey-padel-custom-390-hero.jpg) | [Lihat](checklist-pesan-jersey-padel-custom-1440-article.jpg) | [Lihat](checklist-pesan-jersey-padel-custom-390-article.jpg) |
| Homepage | [Lihat](index-1440-hero.jpg) | [Lihat](index-390-hero.jpg) | [Card Padel](index-1440-padel-card.jpg) | [Card Padel](index-390-padel-card.jpg) |

Hasil terstruktur: [browser](browser-results.json), [anchor](anchor-results.json), [SEO/link](static-results.json), dan [editorial/regresi](editorial-regression-results.json).

## Mengulang pemeriksaan

```powershell
python scripts/qa_padel.py
& 'C:/Users/toviq13/AppData/Local/Python/pythoncore-3.14-64/python.exe' scripts/qa_padel_browser.py --output <folder-bukti-baru>
git diff --check
```

Gunakan folder bukti baru jika ingin mempertahankan hasil pengujian ini. Browser QA memerlukan Playwright dan Chromium yang telah tersedia. Tidak ada masalah tersisa dari cakupan pengujian ini; pengujian menggunakan Chromium desktop dan viewport mobile, bukan perangkat fisik atau semua mesin browser.
