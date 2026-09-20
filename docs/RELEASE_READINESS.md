# Penyelesaian audit persiapan release

[README utama](../README.md) · [Verifikasi lokal](VALIDATION.md) · [Draf release](PORTFOLIO_RELEASE.md)

Paket perbaikan berdasarkan baseline `0fa0c24e508f0221a2dae8044da17c3d7317e2bc` pada `mpnabil95/student-success-prediction`. Pemeriksaan dan perbaikan disiapkan pada 20 September 2026. Belum ada tag, release, atau perubahan remote yang diterbitkan oleh pembuat paket.

## Temuan dan penyelesaian

| Temuan | Perbaikan | Bukti lokal |
|---|---|---|
| R1 — CSV dengan field berlebih dapat bergeser karena implicit index pandas | Record dibaca memakai parser CSV strict; jumlah field harus sama dengan header sebelum dibuat DataFrame. Header kosong/ganda, field kurang, dan kutipan tidak lengkap ditolak. | Enam tes regresi CSV: kedua delimiter, field tambahan di awal/akhir, record pendek, nilai quoted multiline, serta batas ukuran/baris. |
| R2 — Codespaces tidak sesuai Python dan setup dapat menutupi kegagalan | Image Python 3.12; instalasi menggunakan interpreter yang sama dan `&&`; proteksi CORS/XSRF bawaan tidak dinonaktifkan. | JSON dan perintah diperiksa; Python lokal 3.12 serta `pip check` berhasil. Build Codespaces aktual belum dijalankan. |
| R3 — CI melatih ulang sebelum memeriksa file checkout | Dua job: validasi paket commit dahulu, lalu build/reproduksi dengan snapshot referensi. Verifier gagal bila ada skip dan tidak menulis laporan dalam mode read-only. | Paket lolos gate; tiga tes merusak salinan metrik, probabilitas, atau execution count dan berhasil mendeteksi kerusakan. |
| R4 — Dokumentasi tertinggal dari implementasi | Link demo, cakupan 39 tes, riwayat UI, panduan input/reproduksi/folder, dan template release diperbarui bersama generatornya. | Generator dokumen serta pemeriksaan tautan lokal dijalankan. |

## Bukti paket

- 39 tes lulus tanpa skip: 15 kontrak, 6 CSV, 3 gate paket, 10 Streamlit AppTest, dan 5 aset UI. Hasil bertanggal di `reports/verification.json`.
- Builder notebook selesai dengan 41 sel total dan 28 sel kode dieksekusi melalui Python biasa. Struktur nbformat, urutan eksekusi, sintaks, dan output tersimpan diperiksa.
- Seluruh 1.770 baris prediksi policy validation/holdout cocok dengan model tersimpan; metrik dan 91 kandidat threshold dihitung ulang untuk pemeriksaan.
- Perbaikan parser tidak mengubah skenario, fitur, model terpilih, threshold 0,19, atau hasil evaluasi. Hash sumber manifest diperbarui melalui training yang benar-benar dijalankan.
- Build kedua dibandingkan dengan snapshot paket: metrik, sembilan tabel, sumber notebook, serta dokumen generator konsisten dalam toleransi yang tercantum di panduan reproduksi.
- `pip check` berhasil pada lingkungan lokal. Konfigurasi workflow/container diperiksa secara statis; ini bukan klaim bahwa container atau job GitHub baru telah berjalan.

## Batas verifikasi dan langkah pemilik sebelum tag

1. Terapkan paket ke clone repository, periksa diff, lalu commit dan push sendiri.
2. Pastikan **Check committed package** dan **Reproduce the experiment** berhasil pada commit yang sama di Actions. Bukti CI baseline run `35210959197` tidak mencakup workflow baru ini.
3. Rebuild Codespaces jika memakai lingkungan tersebut. Periksa Python 3.12 dan preview aplikasi, karena build container nyata belum diuji dari lingkungan pembuat paket.
4. Setelah deployment diperbarui, coba empat halaman pada desktop dan ponsel; buka/tutup sidebar, unggah template, pastikan baris yang rusak ditolak, unduh hasil, dan periksa confusion matrix. Audit browser baseline telah memeriksa alur dasar desktop, tetapi belum seluruh upload/download atau ukuran layar.
5. Jika pemeriksaan tersebut berhasil, buat tag pada commit yang lolos dan gunakan draf `PORTFOLIO_RELEASE.md`. Jangan gunakan tag arsip Dicoding untuk versi portofolio.

Eksekusi kernel Jupyter terpisah pada lingkungan audit tidak berhasil memulai kernel karena pembatasan socket/interface. Ini dicatat sebagai batas lingkungan; builder Python berhasil dan tidak diklaim sebagai pengujian kernel Jupyter.

## Batas model yang tetap berlaku

Perbaikan ini menutup masalah rekayasa paket yang ditemukan, bukan membuktikan model sempurna. Evaluasi tetap retrospektif pada holdout historis yang pernah diperiksa; belum ada validasi eksternal. Kelas Enrolled masih lemah. Hasil peninjauan memerlukan konfirmasi manusia dan tidak dipakai untuk keputusan akademik otomatis.
