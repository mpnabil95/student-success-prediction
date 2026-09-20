# Peta repository — mulai dari tujuanmu

[README utama](../README.md) · [Indeks dokumentasi](README.md) · [Panduan aplikasi](APP_GUIDE.md)

Repository ini menggabungkan sebuah studi analisis dan aplikasi yang memakai hasil studi tersebut. Banyaknya file berasal dari pemisahan data sumber, kode, model, bukti evaluasi, dan penjelasan. Kamu tidak perlu memahami semuanya untuk mulai menggunakan project.

## Tiga jalur membaca

| Tujuan | Urutan yang disarankan |
|---|---|
| Memahami portofolio | README utama → BUSINESS_CASE → hasil/model card → notebook bila ingin detail |
| Mencoba aplikasi | Petunjuk instalasi di README utama → APP_GUIDE → template di examples |
| Mengembangkan project | Panduan ini → schema/inference atau modeling/train → REPRODUCIBILITY → tests |

Untuk menemukan satu file tertentu, buka README foldernya melalui tabel berikut. README folder menyebut setiap file langsung di dalamnya, fungsi, dan kapan perlu dibuka. Khusus `.github/`, gunakan `GUIDE.md` agar README utama tetap tampil pada beranda repository.

## Hubungan antar-folder

| Peran | Folder | Cara memahaminya |
|---|---|---|
| Bahan awal | [data/](../data/README.md) dan [data/raw/](../data/raw/README.md) | Catatan historis yang menjadi sumber eksperimen |
| Aturan dan proses | [student_success/](../student_success/README.md) | Kode yang memvalidasi input, melatih model, memprediksi, dan membuat grafik |
| Hasil training untuk aplikasi | [artifacts/](../artifacts/README.md) | Model terlatih dan identitas/kontraknya |
| Bukti hasil eksperimen | [reports/](../reports/README.md) dan [reports/figures/](../reports/figures/README.md) | Tabel, metrik, prediksi evaluasi, dan grafik |
| Penjelasan untuk manusia | [docs/](README.md) | Konteks, panduan, metodologi, batas penggunaan, dan riwayat |
| Otomatisasi lokal | [scripts/](../scripts/README.md) | Perintah untuk membangun notebook/dokumen dan memeriksa paket |
| Bahan percobaan | [examples/](../examples/README.md) | Input sintetis untuk mencoba aplikasi |
| Pemeriksaan perilaku | [tests/](../tests/README.md) | Tes otomatis aturan data, model, dan sebagian alur aplikasi |
| Otomatisasi GitHub | [.github/](../.github/GUIDE.md) dan [workflows/](../.github/workflows/README.md) | Perintah pemeriksaan pada runner GitHub Actions |
| Tampilan dan pengaturan app | [.streamlit/](../.streamlit/README.md) | Tema dan pengaturan unggahan |
| Lingkungan pengembangan | [.devcontainer/](../.devcontainer/README.md) | Python 3.12 dan setup aplikasi untuk Codespaces |

Saat **training**, kode membaca `data/raw/` dan menghasilkan `artifacts/`, `reports/`, serta template sintetis. Saat **prediksi**, `app.py` memakai kode `student_success/` untuk membaca artefak dan memproses masukan pengguna. Dashboard membaca dataset historis, sedangkan halaman kinerja membaca laporan.

`notebook.ipynb` adalah narasi eksperimen beserta kode dan hasilnya. `scripts/build_notebook.py` dapat membuat ulang notebook tersebut sambil menjalankan training. Notebook tidak harus dijalankan sebelum aplikasi digunakan, karena artefak terlatih sudah disertakan.

## Setiap file pada root

Root adalah folder paling atas, tempat `app.py` berada. Perintah terminal dalam dokumentasi dijalankan dari sini.

| File | Fungsi | Cara memperbarui |
|---|---|---|
| [README.md](../README.md) | Pintu masuk: tujuan, skenario, hasil, navigasi, dan cara menjalankan project | Sunting manual; blok metrik di antara penanda diperbarui build_docs |
| [app.py](../app.py) | Empat halaman Streamlit dan alur interaksi pengguna | Sunting kode, kemudian periksa pengujian aplikasi |
| [notebook.ipynb](../notebook.ipynb) | Narasi analisis, kode, tabel, dan grafik yang sudah dieksekusi | Perbarui builder bila ingin perubahan bertahan saat pembangunan ulang |
| [requirements.txt](../requirements.txt) | Versi dependensi aplikasi dan machine learning | Perubahan perlu uji kompatibilitas dengan artefak model |
| [requirements-notebook.txt](../requirements-notebook.txt) | Dependensi aplikasi ditambah alat Jupyter/notebook | Sunting dan periksa instalasi/eksekusi notebook |
| [pyproject.toml](../pyproject.toml) | Metadata paket, build backend, dan batas versi Python | Sunting untuk perubahan metadata paket; dependensi tetap ada di requirements |
| [CITATION.cff](../CITATION.cff) | Nama, pengembang, versi, URL, dan rujukan dataset untuk sitasi | Sunting saat identitas atau versi project berubah |
| [LICENSE](../LICENSE) | Ketentuan MIT untuk kode | Rujukan lisensi kode; tidak menggantikan lisensi dataset |
| [.gitignore](../.gitignore) | Daftar file lokal yang tidak disertakan dalam Git, misalnya environment dan secrets | Sunting bila ada keluaran lokal baru yang perlu diabaikan |
| [.gitattributes](../.gitattributes) | Aturan teks/biner dan akhir baris untuk menjaga konsistensi lintas OS | Ubah dengan mempertimbangkan checksum data dan file biner |
| [.python-version](../.python-version) | Versi Python yang dituju project | Selaraskan dengan requirements, pyproject, dan workflow |

Nama file yang diawali titik seperti `.gitattributes` tetap bagian dari konfigurasi project. Sertakan ketika menyalin project, sesuai isi repository.

## Mana yang boleh diedit?

| Kelompok | Perlakuan |
|---|---|
| Dokumentasi manual dan README folder | Boleh disunting langsung; periksa tautan dan konsistensi dengan implementasi |
| Kode dan konfigurasi | Sunting sesuai perubahan yang diinginkan, lalu jalankan pemeriksaan yang relevan |
| Dataset mentah | Pertahankan snapshot; perubahan harus disertai versi/provenance dan evaluasi baru |
| Model dan manifest | Hasilkan bersama melalui training; jangan mengganti threshold atau checksum secara manual |
| Laporan evaluasi dan grafik | Hasilkan dari pipeline; jangan menyunting angka hasil untuk memperbaiki tampilan skor |
| Notebook dan dokumen yang dihasilkan script | Ubah sumber builder/template agar revisi tidak hilang ketika dibangun ulang |

Menambah README di folder tidak mengubah jalur impor Python atau lokasi model. File lama dipertahankan di tempatnya agar aplikasi, notebook, dan tautan tetap sesuai struktur yang digunakan.

## Kamus singkat

| Istilah | Penjelasan sederhana |
|---|---|
| Fitur / feature | Informasi masukan seperti nilai semester atau program studi |
| Target / label | Hasil yang ingin diprediksi; di sini Dropout, Enrolled, atau Graduate |
| Training | Proses mempelajari pola dari data |
| Inference | Menggunakan model yang sudah dilatih untuk memprediksi input |
| Artifact | File keluaran training yang diperlukan untuk memakai model |
| Manifest | Kartu identitas artefak beserta versi dan informasi pendukung |
| Schema | Aturan nama kolom, tipe nilai, kategori, dan hubungan antar-input |
| Pipeline | Rangkaian pemrosesan data dan model dalam satu alur |
| Cross-validation / CV | Evaluasi berulang dengan membagi data development ke beberapa fold |
| Holdout | Bagian data yang dipakai mengevaluasi model setelah pilihan dikunci; holdout project ini pernah dilihat pada submission lama |
| Calibration | Penyesuaian probabilitas agar lebih sesuai dengan frekuensi kejadian pada data kalibrasi |
| Threshold / ambang | Nilai batas probabilitas untuk menetapkan perlu peninjauan atau pemantauan rutin |
| Recall | Bagian kasus Dropout aktual yang berhasil ditandai |
| Precision | Bagian profil yang ditandai dan memang berstatus Dropout |
| Macro F1 | Rata-rata F1 ketiga kelas dengan bobot sama untuk setiap kelas |
| Review rate | Bagian seluruh profil yang ditandai untuk ditinjau |
| Checksum | Sidik jari isi file untuk mendeteksi perubahan byte; bukan bukti keaslian penerbit |
| CI | Pemeriksaan otomatis saat perubahan dikirim ke GitHub |
| `.md` | Dokumen Markdown yang dapat dibaca langsung pada GitHub |
| `.ipynb` | Notebook berisi teks, kode, dan keluaran; dapat dibuka di Jupyter/VS Code |
| `.csv` / `.json` | Tabel teks / data terstruktur yang dapat dibaca program |
| `.joblib` | Model biner yang dimuat program; hanya gunakan sumber tepercaya |
| `.png` / `.svg` | Gambar raster / gambar vektor |

## Menjaga dokumentasi tetap mudah dibaca

Saat menambah file, tuliskan fungsinya di README folder terkait. Tambahkan README baru jika subfolder mempunyai tujuan tersendiri, banyak isi, atau membutuhkan aturan khusus. Tidak perlu membuat satu README untuk setiap file atau mengulang penjelasan teknis lengkap di semua tingkat.

Pertahankan penjelasan ringkas di README utama, rincian file di README folder, dan alasan metodologis di dokumen khusus. Setelah mengubah struktur, periksa tautan relatif dan perintah yang menggunakan path lama. Aturan regenerasi dokumentasi ada di [scripts/README.md](../scripts/README.md).

## Pengecualian untuk folder .github

GitHub memilih README beranda dari `.github`, lalu root, kemudian `docs`. Karena itu dokumentasi langsung dalam `.github/` bernama [GUIDE.md](../.github/GUIDE.md), bukan `README.md`. README di `.github/workflows/` dan folder lain tetap dapat digunakan. Jangan membuat kembali `.github/README.md` untuk indeks folder.

Sumber: [GitHub Docs — About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes).
