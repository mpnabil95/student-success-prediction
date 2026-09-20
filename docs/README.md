# Dokumentasi — indeks dan urutan membaca

[Kembali ke README utama](../README.md) · [Peta repository](../docs/REPOSITORY_GUIDE.md)

Folder ini menjelaskan alasan, cara penggunaan, bukti, dan riwayat project. Tidak semua dokumen perlu dibaca sekaligus. Untuk pembaca baru, mulai dari peta repository atau panduan aplikasi.

## Isi folder

| File atau folder | Fungsi | Kapan dibuka |
|---|---|---|
| [REPOSITORY_GUIDE.md](REPOSITORY_GUIDE.md) | Peta file root, hubungan antar-folder, jenis file, dan kamus istilah. | Pertama kali membuka repository atau bingung memilih file. |
| [UI_CHANGELOG.md](UI_CHANGELOG.md) | Perubahan antarmuka, dependensi, cakupan pengujian, dan pemeriksaan visual yang masih diperlukan. | Memahami versi antarmuka terbaru atau menyiapkan deployment. |
| [APP_GUIDE.md](APP_GUIDE.md) | Langkah penggunaan empat halaman, input CSV, arti hasil, dan kendala umum. | Ingin mencoba aplikasi atau memahami output prediksi. |
| [BUSINESS_CASE.md](BUSINESS_CASE.md) | Masalah, pengguna, skenario prediksi, keputusan desain, dan rancangan pilot. | Menilai tujuan dan manfaat yang ingin dicapai. |
| [DATA_CARD.md](DATA_CARD.md) | Asal dataset, snapshot, checksum, label target, lisensi, dan batas generalisasi. | Memahami data dan kelayakan penggunaannya. |
| [FEATURE_DICTIONARY.md](FEATURE_DICTIONARY.md) | Kamus 14 fitur, skala nilai, kode kategori, dan aturan validasi. | Mengisi formulir atau mempersiapkan CSV. |
| [MODEL_CARD.md](MODEL_CARD.md) | Model, protokol, metrik per kelas, interval, diagnosis kelompok, dan batas penggunaan. | Mengevaluasi kemampuan dan kelemahan model. |
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | Tahapan eksperimen, dependensi, keluaran, dan aturan pembaruan model. | Mengulang training atau memeriksa metodologi teknis. |
| [VALIDATION.md](VALIDATION.md) | Catatan verifikasi lokal terakhir, dihasilkan verifier. | Memeriksa apa yang benar-benar diuji dan apa yang belum. |
| [RELEASE_READINESS.md](RELEASE_READINESS.md) | Penyelesaian empat temuan audit, bukti, dan langkah sebelum tag. | Menyiapkan commit dan release portofolio. |
| [AUDIT_REMEDIATION.md](AUDIT_REMEDIATION.md) | Temuan audit submission serta tindak lanjut di versi portofolio. | Memahami alasan perubahan dari project lama. |
| [MIGRATION.md](MIGRATION.md) | Panduan historis mengganti isi main dari submission ke versi portofolio. | Memahami migrasi awal; bukan instruksi rutin untuk setiap pembaruan. |
| [DICODING_RELEASE_CLEAN.md](DICODING_RELEASE_CLEAN.md) | Draf teks release arsip submission Dicoding. | Menyunting deskripsi release arsip jika diperlukan. |
| [PORTFOLIO_RELEASE.md](PORTFOLIO_RELEASE.md) | Draf catatan release versi portofolio beserta syarat verifikasinya. | Menyiapkan release; keberadaan file tidak berarti release telah diterbitkan. |


## Jalur membaca

- **Pembaca umum:** README utama → BUSINESS_CASE → APP_GUIDE.
- **Reviewer Data Science:** DATA_CARD → FEATURE_DICTIONARY → notebook → MODEL_CARD → laporan evaluasi.
- **Pengembang:** REPOSITORY_GUIDE → README kode inti → REPRODUCIBILITY → README tests.
- **Riwayat submission:** AUDIT_REMEDIATION → MIGRATION → draf release arsip.

## Mana yang dihasilkan otomatis?

`MODEL_CARD.md`, `FEATURE_DICTIONARY.md`, dan `PORTFOLIO_RELEASE.md` ditulis ulang oleh `python scripts/build_docs.py`. Ubah template script tersebut bila perubahan perlu bertahan setelah regenerasi. `VALIDATION.md` ditulis ulang oleh `python scripts/verify_package.py` untuk catatan verifikasi lokal.

Dokumen lainnya dan README folder disunting manual. README utama juga disunting manual, kecuali blok metrik yang diberi penanda. [Panduan scripts](../scripts/README.md) merinci urutan perintah dan keluaran yang terdampak.
