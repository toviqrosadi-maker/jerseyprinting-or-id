# JerseyPrinting.or.id — Cluster Jersey Padel Custom v4.7

Status: **READY FOR REVIEW** (source lokal; belum push atau deploy).

Pembaruan 7 November 2026: FINAL QA browser telah dijalankan dan masalah anchor yang tertutup header telah diperbaiki. Lihat [laporan FINAL QA](qa-padel-final/README.md) untuk hasil terbaru dan screenshot. Catatan keterbatasan browser di bawah merupakan keadaan pemeriksaan awal pada 6 November.

Tanggal pemeriksaan: 6 November 2026, Asia/Jakarta.

Branch: `feat/jersey-padel-cluster`. Branch khusus ini sudah tersedia saat pekerjaan dimulai dan working tree awal bersih. Baseline: `0bee568b1a2e479c0b203775cd22db2560fff23d`. Commit implementasi dapat dilihat dengan `git log -1 --oneline` pada branch tersebut.

## File baru dan jumlah kata

Hitungan menggunakan teks terlihat dalam `<article class="article">`: isi, heading, daftar, FAQ, dan CTA akhir. Header, footer, sidebar, breadcrumb, teks hero, metadata, serta atribut/link URL tidak dihitung. Kata berhubung dihitung satu unit.

| File baru | Kata | Intent dan sudut pembahasan |
| --- | ---: | --- |
| `jersey-padel-custom.html` | 2.163 | Pilar komersial-informatif: produk, bahan, desain, ukuran, pemesanan, FAQ, konsultasi |
| `bahan-jersey-padel.html` | 1.240 | Membandingkan sampel kain berdasarkan kenyamanan dan penggunaan |
| `desain-jersey-padel-custom.html` | 1.249 | Menyusun brief visual, warna, hierarki, serta pemeriksaan mockup |
| `ukuran-jersey-padel-pria-wanita.html` | 1.258 | Pengukuran pakaian, pola, kelonggaran, dan pengumpulan ukuran tim |
| `jersey-padel-full-printing-sublimasi.html` | 1.281 | Proses cetak, file, bahan, warna, dan batas sambungan panel |
| `jersey-padel-komunitas.html` | 1.229 | Keputusan kelompok, pilihan anggota, pengelolaan data, pesanan tambahan |
| `jersey-padel-turnamen.html` | 1.282 | Ketentuan acara, tenggat, perubahan peserta, dan distribusi sebelum tanding |
| `jersey-padel-lengan-panjang-pendek.html` | 1.268 | Perbandingan model, penutupan, lapisan dalam, dan ruang gerak |
| `jersey-padel-nama-logo-sponsor.html` | 1.293 | Persiapan aset, ejaan, izin penggunaan, hierarki sponsor, dan persetujuan |
| `cara-merawat-jersey-padel.html` | 1.260 | Rutinitas setelah bermain, label perawatan, pencucian, pengeringan, penyimpanan |
| `checklist-pesan-jersey-padel-custom.html` | 1.264 | Titik pemeriksaan dari brief, penawaran, persetujuan hingga penerimaan |

File pendukung baru: `scripts/qa_padel.py` dan `docs/seo-padel-review.md`.

## File lama yang diubah

- `index.html`: hanya tujuan link detail card Jersey Padel di `#produk`, menjadi `/jersey-padel-custom.html`. Card olahraga lain dan seluruh teks/metadata homepage tetap sama.
- `printing-jersey-bandung.html`: satu paragraf kontekstual tentang kain, pola, dan kebutuhan gerak padel pada bagian pemilihan bahan.
- `jasa-pembuatan-jersey-bandung.html`: satu paragraf kontekstual tentang kebutuhan khusus klub padel pada bagian jenis jersey.
- `bahan-jersey-full-printing.html`: satu paragraf yang menghubungkan evaluasi bahan dengan ukuran dan model padel.
- `tips-desain-jersey-tim.html`: satu paragraf tentang identitas klub padel dan keterbacaan panel pada bagian hierarki visual.
- `sitemap.xml`: 11 URL baru, total 36 URL; seluruh URL lama dipertahankan.

CSS, JavaScript, gambar lama, `robots.txt`, `vercel.json`, redirect, canonical halaman lama, serta seluruh URL lama tidak diubah. Tidak ada dependensi atau konfigurasi build baru.

## QA yang dijalankan

```powershell
python scripts/qa_padel.py
python -m http.server 18747 --bind 127.0.0.1 --directory C:/Users/toviq13/jerseyprinting-or-id
python scripts/qa_padel.py --http-base http://127.0.0.1:18747/
git diff --check
```

Semua pemeriksaan akhir di atas lulus. Server hanya dipakai untuk smoke test lokal, bukan publikasi.

| Pemeriksaan | Hasil |
| --- | --- |
| Ketersediaan 11 halaman baru | 11/11 berkas ada dan GET HTTP lokal 200 |
| Homepage, CSS, JS, visual padel, sitemap | GET HTTP lokal 200 pada kelima target |
| Link/aset lokal seluruh situs | 1.296 referensi diperiksa pada 37 HTML dan CSS; tidak ada path/aset/fragment rusak |
| Title | Tidak ada duplikat pada 37 HTML |
| Canonical | Tidak ada duplikat; domain canonical yang ada konsisten WWW; 11 halaman baru self-canonical |
| Meta description | Unik pada 11 halaman baru, panjang 138–153 karakter |
| H1 dan heading | Satu H1 per halaman baru, H1 unik, tidak ada lompatan level heading atau ID ganda |
| Indexability | Halaman baru memakai `index,follow,max-image-preview:large`; robots dan konfigurasi lama tetap |
| Open Graph dan JSON-LD | URL sesuai canonical; JSON valid, Article untuk artikel pendukung dan WebPage untuk pilar |
| Alt gambar | Semua gambar halaman baru memiliki alt yang terisi |
| WhatsApp | Seluruh link WA halaman baru tetap menuju nomor situs `6281221111398` |
| Link pilar ↔ artikel | Pilar menautkan seluruh 10 artikel; setiap artikel menautkan kembali secara kontekstual |
| Link antarartikel | Setiap artikel mempunyai 2–4 link kontekstual ke artikel pendukung lain |
| Link homepage | Seluruh isi halaman baru mempunyai link `/` dengan anchor tepat `jersey printing` |
| Link dari halaman lama | Empat halaman lama memiliki link pilar di paragraf pembahasan |
| Regresi homepage | Perbandingan utuh terhadap baseline membuktikan hanya href card Padel berubah |
| Regresi halaman lama | Setelah satu paragraf tambahan dilepas, isi setiap halaman identik dengan baseline |
| Sitemap | Tepat 11 penambahan; tidak ada duplikat atau penghapusan URL lama |
| Kebersihan diff | `git diff --check` lulus |

QA dapat diulang tanpa server dengan perintah pertama. Mode `--http-base` bersifat opsional dan dibatasi ke localhost. Script menggunakan pustaka standar Python, tanpa instalasi paket.

## Kualitas dan kemiripan konten

Pembuka, heading, contoh situasi, dan penutup ditulis sesuai intent tiap artikel. Materi komersial umum diringkas pada pilar; artikel pendukung memperinci keputusan spesifik. Tidak ada paragraf isi identik sepanjang minimal 25 kata antarhalaman baru. Kemiripan pasangan tertinggi berdasarkan Jaccard urutan lima kata adalah **0,265%**, antara pilar dan artikel desain. Angka tersebut mengukur pengulangan tekstual, bukan skor plagiarisme eksternal atau jaminan penilaian mesin pencari.

Review editorial juga memeriksa agar tidak ada tabel ukuran rekaan, harga, klaim kapasitas, garansi, atau kepastian jadwal yang belum diverifikasi. Pilihan minimum pesanan, stok bahan, model, serta jadwal diarahkan untuk dikonfirmasi. Ketentuan turnamen diarahkan ke penyelenggara acara yang diikuti.

Untuk penjelasan teknis sublimasi, artikel terkait mengacu pada [panduan Epson](https://epson.com/sublimation-printers-for-makers). Artikel perawatan mengacu pada [GINETEX](https://www.ginetex.ch/en/) untuk memahami simbol perawatan; petunjuk produk aktual tetap menjadi acuan. Tidak ada klaim bahwa setiap jersey memakai teknologi atau sertifikasi tertentu.

## Desain, aset, dan batas pengujian

Halaman baru memakai kelas dan komponen yang sudah ada: `page-hero`, `cluster-hero-grid`, `article-wrap`, `article`, `toc`, `faq`, tombol, header, footer, dan navigasi mobile. Sidebar pilar diringkas agar daftar isi tidak terlalu panjang. Tidak ada perubahan CSS global atau aset halaman lama.

Visual `assets/images/product-padel-new.webp` sudah tersedia, telah diperiksa secara visual, dan sesuai topik pemain padel. Dimensi gambar 600 × 520. Aset digunakan tanpa menambah gambar baru; caption menjelaskan bahwa ini ilustrasi situs, bukan dokumentasi pesanan pelanggan.

**Desktop 1440px dan mobile 390px: belum diuji di browser.** Inventori browser sesi ini kosong dan native computer automation tidak tersedia. Pemeriksaan source memastikan komponen menggunakan CSS responsif situs yang sama, tetapi tidak menggantikan screenshot atau uji interaksi. Tidak ada klaim lulus pengujian visual.

## Tindak lanjut review

1. Jalankan pemeriksaan visual pada viewport 1440px dan 390px saat browser tersedia: hero, wrapping heading, sidebar, menu mobile, FAQ, dan CTA WhatsApp.
2. Foto produk padel asli dan detail kain/printing dapat ditambahkan bila tersedia serta sesuai izin penggunaannya. Ini peningkatan aset opsional; saat ini tidak ada referensi gambar fiktif atau rusak.
3. Review editorial dan bisnis dapat mengonfirmasi opsi aktual tanpa perlu menambahkan angka harga atau janji baru.

Belum ada push, PR jarak jauh, perubahan Production, atau deploy. Review source dapat dimulai dari branch lokal ini.
