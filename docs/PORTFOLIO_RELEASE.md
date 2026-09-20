# v1.0.0 — Student Success Portfolio Edition

Versi portofolio pertama mengembangkan baseline submission Dicoding menjadi studi kasus prediksi status studi dengan informasi sampai akhir semester 1.

## Perubahan utama

- Skenario dan kontrak 14 fitur ditetapkan; seluruh fitur semester 2 dikeluarkan.
- Seleksi model melalui cross-validation dan kalibrasi di dalam training.
- Pemilihan threshold pada policy validation yang terpisah.
- Model, schema, dan manifest konsisten untuk training serta inference.
- Dashboard historis, prediksi individu/batch, dan halaman kinerja dalam satu aplikasi.
- Notebook sudah dijalankan; laporan metrik, error kelompok, importance, dan figur disertakan.
- Validasi domain, relasi akademik, preset, dan kesetaraan batch/individu diuji.
- Parser CSV menolak baris berlebih/kurang kolom, kutipan rusak, serta header kosong atau duplikat sebelum inference.
- Ikon lokal, kontrol sidebar, kontras, dan rendering confusion matrix diperbaiki pada dashboard.
- Codespaces memakai Python 3.12, instalasi berhenti saat gagal, dan proteksi CORS/XSRF bawaan tetap aktif.
- CI memeriksa paket yang di-commit sebelum training, lalu membandingkan hasil reproduksi dengan snapshot commit tersebut.
- Peta repository, panduan folder, dan bukti verifikasi diperbarui.

## Hasil

Model terpilih `random_forest`. Macro F1 holdout historis 0.6129. Pada threshold 0.19, recall peninjauan Dropout 88.03%, precision 54.82%, dan review rate 51.53%.

Hasil bersifat retrospektif pada holdout yang pernah dilihat dalam proyek lama. Tidak ada klaim validasi eksternal atau keberhasilan intervensi.

## Menjalankan

Gunakan Python 3.12, instal `requirements.txt`, lalu jalankan `streamlit run app.py`. Artefak sudah tersedia; panduan lengkap di README. [Buka demo](https://student-success-prediction-95.streamlit.app/).

## Verifikasi sebelum publikasi release

Lihat [hasil verifikasi lokal](VALIDATION.md) dan [kesiapan release](RELEASE_READINESS.md). Kedua job CI harus berhasil pada commit yang akan ditag. Dokumen ini adalah draf release; publikasi tag/release dilakukan pemilik repository.

Arsip submission tetap pada `dicoding-submission-v1.0.0`.
