# Pemasangan hero dan banner CTA pilar padel

**PASS — READY FOR REVIEW.** Branch: `feat/jersey-padel-cluster`. Baseline: `4ad3f34`. Tanggal: 7 November 2026, Asia/Jakarta. Belum push, merge, atau deploy.

## Sumber dan konversi

Kedua JPG disalin dari folder backup berikut ke `assets/images/` repo aktif, tanpa mengedit backup:

`E:\BLOG\JERSEYPRINTING OR ID\web\jerseyprinting-or-id-v4.6-FINAL-QA-PASSED\assets\images`

| Sumber JPG | Resolusi sumber → WebP | Byte JPG → WebP | Penghematan |
| --- | --- | --- | --- |
| `Man_holding_padel_racket_b5165b84.jpg` → `jersey-padel-custom-hero.webp` | 1376 × 768 → 1376 × 768 | 736.281 → **282.874** (276,24 KiB) | 61,6% |
| `Custom_padel_jersey_banner_design_f9e218c5.jpg` → `jersey-padel-custom-cta.webp` | 1376 × 768 → 1376 × 768 | 773.239 → **258.290** (252,24 KiB) | 66,6% |

Konversi deterministik memakai encoder WebP Chromium dengan kualitas 0,95. Tidak ada resize, crop, upscale, generasi, atau penajaman buatan. Visual sumber dan hasil WebP diperiksa. Hash JPG salinan identik dengan file sumber di backup:

- Hero: `969350bbc802a88a4b70f0a632bb42bcd2dae0b99fc386a1d429ddcf4325db71`.
- Banner: `958ac69a42f4a68d5e0fd9ba91b2d90c165bf52afc1c9086e2faf0cdb231db05`.

## Perubahan implementasi

- `jersey-padel-custom.html`: hero dan `og:image` memakai WebP baru. Hero mempunyai alt deskriptif, `width="1376"`, `height="768"`, `loading="eager"`, `fetchpriority="high"`, dan `decoding="async"`.
- Banner berada **setelah bagian desain**, sebelum bagian sublimasi, di dalam isi artikel. Seluruh banner dan caption dibungkus link WhatsApp aktif dengan `target="_blank"` dan `rel="noopener"`.
- Banner mempunyai alt deskriptif, dimensi asli, `loading="lazy"`, serta `decoding="async"`.
- `assets/css/padel.css`: aturan khusus `.padel-cta` mempertahankan rasio sumber, meniadakan crop, dan menampilkan teks CTA/nomor dalam HTML 16px. Nomor menggunakan `white-space: nowrap` agar tidak terbelah pada mobile. Aturan lama untuk anchor tetap.

Pesan WhatsApp banner:

> Halo Zipzip, saya ingin konsultasi jersey padel custom untuk tim atau komunitas. Mohon informasi bahan, desain, dan pemesanan.

Tujuan: `https://wa.me/6281221111398` dengan pesan tersebut pada parameter `text`.

## Hasil QA

Chromium melalui Playwright: viewport **1440 × 1000** dan **390 × 844**, masing-masing pada DPR 1 serta DPR 2. Empat kasus lulus. Screenshot ditinjau, termasuk bidang gambar penuh dan konteks penempatan banner.

| Pemeriksaan | Hasil |
| --- | --- |
| Dimensi konversi sama dengan sumber | PASS, kedua gambar tetap 1376 × 768 |
| Hero utuh | PASS, tidak ada crop tambahan; wajah, tangan, dan raket terlihat sesuai bidang foto sumber |
| Banner utuh | PASS, rasio asli dipertahankan tanpa crop/stretch |
| Ukuran hero tampil 1440px / 390px | 481,66 × 268,83 / 356,80 × 199,14 CSS px |
| Ukuran banner tampil 1440px / 390px | 820 × 457,67 / 356,80 × 199,14 CSS px |
| Keterbacaan mobile | PASS, pesan utama dan nomor terlihat pada banner; caption HTML 16px menegaskan pesan dan kontak tanpa nomor terbelah |
| Klik banner | PASS pada empat kasus; popup menuju nomor dan pesan yang sesuai |
| Uji WhatsApp tanpa pengiriman | PASS, request diintersepsi lokal; tidak mengirim pesan atau request nyata ke WhatsApp |
| Loading dan prioritas | PASS, hero eager/high; banner lazy |
| Alt dan width/height | PASS, kedua gambar memiliki atribut yang sesuai |
| Overflow horizontal dan page error | PASS, tidak ditemukan |
| Paragraf dan heading lama | PASS, identik dengan baseline; hanya caption CTA baru ditambahkan |
| Tautan lama | PASS, seluruh href lama tetap; ditambahkan satu tautan banner |
| Title, meta description, canonical | PASS, tetap; hanya `og:image` diperbarui mengikuti hero |
| Halaman lain, sitemap, robots, Vercel, CSS global, JS utama | PASS, tidak berubah |
| QA SEO/link seluruh situs | PASS, 1.308 referensi lokal tanpa broken link/aset |
| Diff whitespace | PASS, `git diff --check` |

Resolusi hero baru cukup untuk bidang tampil pada DPR 2 di kedua viewport. Banner memakai sumber asli tanpa upscale; caption HTML tetap tajam dan terbaca terlepas dari kepadatan layar. Sepuluh artikel pendukung tetap memakai aset sebelumnya sesuai ruang lingkup permintaan yang hanya memasang gambar pada pilar.

## Screenshot

| Bukti | 1440px | 390px |
| --- | --- | --- |
| Hero halaman, DPR 1 | [Lihat](pillar-1440-dpr1-hero.jpg) | [Lihat](pillar-390-dpr1-hero.jpg) |
| Gambar hero penuh, DPR 1 | [Lihat](pillar-1440-dpr1-hero-image.png) | [Lihat](pillar-390-dpr1-hero-image.png) |
| Banner dan caption, DPR 1 | [Lihat](pillar-1440-dpr1-cta.png) | [Lihat](pillar-390-dpr1-cta.png) |
| Konteks banner, DPR 1 | [Lihat](pillar-1440-dpr1-cta-context.jpg) | [Lihat](pillar-390-dpr1-cta-context.jpg) |
| Gambar hero penuh, DPR 2 | [Lihat](pillar-1440-dpr2-hero-image.png) | [Lihat](pillar-390-dpr2-hero-image.png) |
| Banner dan caption, DPR 2 | [Lihat](pillar-1440-dpr2-cta.png) | [Lihat](pillar-390-dpr2-cta.png) |

Detail dimensi, hash, atribut, tujuan klik, serta hasil regresi: [pillar-assets-results.json](pillar-assets-results.json).

## File dibuat dan diubah

Diubah: `jersey-padel-custom.html`, `assets/css/padel.css`.

Dibuat:

- Dua JPG sumber yang disalin ke `assets/images/`.
- `assets/images/jersey-padel-custom-hero.webp` dan `assets/images/jersey-padel-custom-cta.webp`.
- `scripts/prepare_padel_assets.py` untuk konversi ulang pada dimensi asli.
- `scripts/qa_padel_pillar_assets.py` untuk QA gambar, CTA, dan regresi.
- Laporan ini, JSON hasil, serta screenshot dalam `docs/qa-padel-new-assets/`.

Perintah pemeriksaan:

```powershell
& 'C:/Users/toviq13/AppData/Local/Python/pythoncore-3.14-64/python.exe' scripts/qa_padel_pillar_assets.py --output <folder-bukti-baru>
python scripts/qa_padel.py
git diff --check
```

File backup tidak ditulis oleh skrip. Pekerjaan disiapkan untuk review lokal, tanpa push atau deploy.
