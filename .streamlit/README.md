# Streamlit — konfigurasi aplikasi

[Kembali ke README utama](../README.md) · [Peta repository](../docs/REPOSITORY_GUIDE.md)

Folder ini mengatur tampilan dan perilaku dasar Streamlit. Logika prediksi berada di paket `student_success`, sedangkan halaman aplikasi berada di `app.py`.

## Isi folder

| File atau folder | Fungsi | Kapan dibuka |
|---|---|---|
| [styles.css](styles.css) | Warna, tipografi, panel, navigasi, serta aturan tampilan layar kecil. | Menyesuaikan identitas visual aplikasi. |
| [config.toml](config.toml) | Tema terang, warna, font, batas unggahan 10 MB, dan pengaturan statistik penggunaan. | Menyesuaikan tampilan aplikasi atau konfigurasi server. |


## Catatan penyuntingan

`config.toml` dapat disunting manual. Mengubah batas unggahan di sini saja tidak mengubah batas parser CSV atau batas jumlah baris di `student_success/schema.py`; aturan perlu diselaraskan bila kebutuhan berubah.

`gatherUsageStats = false` menonaktifkan pengumpulan statistik penggunaan oleh Streamlit melalui pengaturan tersebut. Itu bukan jaminan privasi menyeluruh untuk layanan hosting.

Aplikasi saat ini tidak membutuhkan API key. Jika kelak memakai secrets, jangan commit `secrets.toml`; path tersebut sudah dikecualikan oleh `.gitignore`. [Panduan aplikasi](../docs/APP_GUIDE.md) menjelaskan alur penggunaan.

## Memelihara tampilan

`app.py` membaca styles.css dari direktori ini. Warna dasar juga diselaraskan dengan config.toml. Container panel memakai `key` Streamlit sebagai kait CSS publik. Beberapa penyesuaian widget tetap bergantung pada atribut frontend Streamlit; periksa ulang tampilan setelah mengganti versi Streamlit. Jangan menghapus indikator fokus keyboard atau tombol pembuka sidebar.

CSS memuat aturan layar kecil dan preferensi reduced motion. Audit baseline memeriksa browser desktop, sidebar, grafik evaluasi/diagnostik, serta alur individu dan batch sintetis. Tampilan semua ukuran layar, pemilih file dan unduhan browser belum diuji menyeluruh. Rincian sejarah perubahan ada di [UI_CHANGELOG.md](../docs/UI_CHANGELOG.md); bukti paket terbaru ada di [RELEASE_READINESS.md](../docs/RELEASE_READINESS.md).
