# Pembaruan antarmuka Student Success

[README utama](../README.md) · [Panduan aplikasi](APP_GUIDE.md) · [Indeks dokumentasi](README.md)

## Perbaikan hover tombol formulir — 21 September 2026

Akar masalah: Streamlit 1.49.1 merender `st.form_submit_button(type="primary")` sebagai `button[kind="primaryFormSubmit"]`. CSS sebelumnya hanya mencakup `kind="primary"`, sehingga style formulir bawaan masih mengambil alih saat hover dan label/ikon kehilangan kontras.

CSS sekarang mencakup kedua jenis tombol pada state normal, hover, fokus keyboard, aktif, dan nonaktif. Hover menggunakan teal `#09685f` dengan teks serta ikon putih. Fokus keyboard mempunyai outline; tombol batch tanpa input tetap nonaktif dengan warna tersendiri. Perubahan terbatas pada tampilan, tanpa training ulang atau perubahan logika prediksi.

Verifikasi lokal pada Streamlit 1.49.1 dan Chromium: bug direproduksi dengan CSS lama pada DOM aplikasi yang sama; CSS baru lulus 8 pemeriksaan state (hover individu, normal, fokus keyboard, aktif, hover sesudah submit, hover pada viewport 390 px, batch nonaktif, batch nonaktif saat hover) ditambah hover batch aktif. Label dan ikon putih terukur pada semua state primer aktif. Submit individu menghasilkan panel hasil dan tombol unduhan. Suite verifikasi paket: 39 tes lulus, 0 gagal/error/skip. Pemeriksaan viewport sempit ini hanya memeriksa tombol; bukan audit mobile menyeluruh. Deployment publik perlu diperiksa setelah pengguna commit dan redeploy.

## Status setelah audit persiapan release — 20 September 2026

Baseline audit: `0fa0c24e508f0221a2dae8044da17c3d7317e2bc`. Versi ini sudah mencakup peningkatan kontras, ikon SVG lokal/fallback tanpa ketergantungan font ikon, kontrol sidebar, serta pemulihan confusion matrix pada Hasil evaluasi. Tes tampilan bertambah menjadi 10 AppTest dan 5 tes aset. Suite lengkap setelah perbaikan audit berjumlah 39 tes lulus tanpa skip.

Perbaikan awal state tombol pada 20 September hanya menyasar `kind="primary"`. Aturan itu tidak cocok dengan tombol formulir Streamlit (`kind="primaryFormSubmit"`), sehingga bug hover pada **Lihat hasil peninjauan** masih terjadi. Perbaikan lanjutannya dicatat di bagian 21 September di atas.

Audit baseline memeriksa browser desktop: Gambaran Data, sidebar, prediksi individu, batch sintetis, confusion matrix, dan diagnostik. Paket perbaikan audit memperketat validasi CSV dan pemeriksaan release; tidak mendesain ulang UI. Pengujian menyeluruh mobile, pemilih file unggahan, unduhan browser, dan deployment commit baru masih perlu dilakukan. Lihat [kesiapan release](RELEASE_READINESS.md).

## Riwayat pembaruan 14 September 2026

Bagian berikut adalah catatan historis berdasarkan commit `97f405ee263ff15f14c802f65d3a2939c3eb73b3`; angka tes dan kendala browser di bawah berlaku pada tanggal tersebut. Tujuannya memperjelas hierarki informasi, memperbaiki pengalaman penggunaan, dan menyajikan hasil dengan identitas visual yang konsisten untuk portofolio.

## Perubahan yang diterapkan

| Bagian | Pembaruan |
|---|---|
| Identitas visual | Kanvas terang, aksen teal, judul halaman, sidebar bermerek, panel dan kartu metrik, warna status konsisten |
| Gambaran Data | Hero berbasis jumlah data nyata; filter program/usia dengan reset; donat komposisi; grafik capaian interaktif; minimum ukuran kelompok dan ekspor ringkasan program |
| Prediksi Individu | Formulir bertab; panel hasil berdampingan; empty state; visual probabilitas; snapshot input; profil tersimpan antarhalaman |
| Prediksi Batch | Pilihan unggahan atau contoh sintetis; validasi; penghapusan hasil saat sumber berubah; filter tindakan; urutan risiko; unduhan lengkap dan terfilter yang dibedakan |
| Kinerja Model | Tab hasil, seleksi, diagnostik, batas penggunaan; confusion matrix, precision-recall, kalibrasi, dan threshold interaktif; konsekuensi TP/FN/FP ditampilkan |
| Interaksi | Fokus keyboard dipertahankan, tombol prediksi tanpa input dinonaktifkan, pesan empty/error/warning diperjelas |
| Pemeliharaan | CSS dipisahkan ke .streamlit/styles.css; helper tampilan tetap di app.py sehingga modul model tidak berubah |

Diagram dan metrik membaca dataset/laporan yang disertakan. Tidak ada metrik peningkatan palsu, prediksi tambahan yang disamarkan sebagai data historis, atau ambang model yang diubah melalui UI.

## Kompatibilitas

- Python 3.12, Streamlit 1.49.1, dan versi inti model tetap sesuai requirements.
- **Altair 5.5.0** sekarang menjadi dependensi langsung untuk grafik interaktif. Jalankan instalasi requirements kembali setelah menyalin pembaruan.
- Sertakan `.streamlit/styles.css` dan `.streamlit/config.toml` bersama `app.py`.
- Dataset, model, schema, manifest, modul `student_success`, dan notebook tetap sama dengan baseline.
- Format hasil prediksi lengkap dipertahankan; ringkasan program dan unduhan terfilter merupakan keluaran tambahan.
- CSS menggunakan key container publik serta beberapa atribut widget Streamlit. Perubahan versi Streamlit memerlukan pemeriksaan tampilan ulang.

## Bukti pengujian

Suite `python -m unittest discover -s tests -v` menghasilkan **23 tes lulus, 0 gagal, 0 error, 0 skip**: 15 kontrak data/model dan 8 regresi UI. Tes UI mencakup:

1. Navigasi empat halaman dan prediksi individu.
2. Filter yang menghasilkan data kosong lalu pemulihan melalui reset.
3. Kesetaraan keluaran individu dengan fungsi inference bersama.
4. Penghapusan hasil lama setelah profil tidak valid dikirim.
5. Penghapusan hasil lama dan pembaruan nilai saat menerapkan preset.
6. Pemulihan profil yang sudah dikirim setelah berpindah halaman.
7. Kesetaraan batch sintetis, filter tindakan, serta urutan peluang Dropout.
8. Penghapusan hasil batch dan penonaktifan tombol saat kembali ke unggahan tanpa file.

Aplikasi Streamlit berhasil dijalankan pada server lokal. Grafik Altair dibangun oleh aplikasi tanpa exception dalam AppTest. Perubahan tidak memerlukan training ulang.

## Batas verifikasi visual dan deployment

Browser pengujian menolak akses server lokal dengan `ERR_BLOCKED_BY_CLIENT`. Karena itu **tampilan desktop/mobile, hasil render grafik di browser, pemilih file unggahan, dan unduhan browser belum diverifikasi langsung**. Tidak ada tangkapan layar yang diklaim sebagai hasil aplikasi. Aturan CSS untuk layar kecil dan reduced motion telah ditambahkan, tetapi belum diuji secara visual.

Sebelum mempublikasikan deployment, coba empat halaman pada browser desktop dan ponsel, periksa sidebar, kontras, tabel dan tooltip, lalu unggah template dan unduh kedua jenis hasil. Gunakan profil sintetis untuk pemeriksaan ini. Bukti CI historis di README tidak berarti patch UI ini sudah lulus CI; periksa run baru setelah commit.

## Sumber implementasi

- [Streamlit 1.49 — container dan CSS key](https://docs.streamlit.io/1.49.0/develop/api-reference/layout/st.container)
- [Streamlit 1.49 — Altair charts](https://docs.streamlit.io/1.49.0/develop/api-reference/charts/st.altair_chart)
- [Altair — arc marks](https://altair-viz.github.io/user_guide/marks/arc.html)
