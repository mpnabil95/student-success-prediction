# Reproduksi dan struktur implementasi

## Alur tunggal

1. Validasi checksum dataset dan schema.
2. Pertahankan split historis 20% sebagai holdout; bagi 80% sisanya menjadi 60% development dan 20% policy validation.
3. Seleksi kandidat terkalibrasi melalui 5-fold CV pada development.
4. Fit kandidat terpilih pada development saja.
5. Pilih threshold dari policy validation.
6. Simpan model, threshold, dan manifest sebelum evaluasi holdout.
7. Hitung holdout metrics, interval, error kelompok, permutation importance, dan figur.
8. Muat ulang artefak untuk prediksi yang sama dengan aplikasi.

Seed 42; split internal memakai seed 43. Kalibrasi sigmoid memakai 3-fold CV di dalam subset training masing-masing. Preprocessing berada di dalam pipeline sehingga tidak dipelajari dari fold evaluasi.

## Menjalankan

Gunakan Python 3.12 dari root repository.

```bash
python -m pip install -r requirements-notebook.txt
python -m student_success.train
python -m unittest discover -s tests -v
streamlit run app.py
```

Notebook interaktif:

```bash
python -m pip install -r requirements-notebook.txt
jupyter lab notebook.ipynb
```

Membangun dan menjalankan notebook secara otomatis tanpa Jupyter:

```bash
python scripts/build_notebook.py
```

Builder menggunakan eksekusi Python biasa, merekam stdout, tabel, dan gambar asli. Semua sel yang dikirim memiliki execution count dan hasil eksekusi. Tidak ada output yang diketik sebagai hasil seolah-olah dijalankan. Jupyter menggunakan sel Python yang sama; builder bukan pengganti pengujian seluruh fitur Jupyter.

## File keluaran

| Path | Fungsi |
|---|---|
| `artifacts/model.joblib` | Calibrated classifier yang benar-benar digunakan aplikasi |
| `artifacts/manifest.json` | Fitur, kelas, threshold, checksum, versi, jumlah split, code hashes |
| `artifacts/feature_schema.json` | Schema semantik dan mapping kategori |
| `reports/protocol.json` | Keputusan eksperimen yang dibekukan |
| `reports/split_assignments.csv` | Membership split per source_row |
| `reports/cv_folds.csv` | Skor setiap fold dan kandidat |
| `reports/model_comparison.csv` | Rerata dan variasi skor CV |
| `reports/threshold_analysis.csv` | Trade-off seluruh threshold pada validation |
| `reports/metrics.json` | Hasil validation, holdout, baseline, dan interval bootstrap |
| `reports/*_predictions.csv` | Prediksi yang dapat dicocokkan kembali ke data sumber |
| `reports/subgroup_metrics.csv` | Diagnosis kelompok setelah model dibekukan |
| `reports/permutation_importance.csv` | Importance global beserta variasinya |
| `reports/figures/` | Grafik PNG dan SVG dari output nyata |

## Reproducibility boundary

Versi inti training dicatat dan dipin: scikit-learn, NumPy, pandas, SciPy, joblib, matplotlib. Python audit adalah 3.12.14. Requirements bukan lockfile semua dependensi transitif; dependensi UI/notebook dan OS masih dapat memengaruhi pengalaman instalasi.

Artefak joblib hanya dimuat dari file lokal proyek yang dipercaya. Model tidak kompatibel secara universal lintas scikit-learn; aplikasi memeriksa versi persis dan checksum. Checksum membantu mendeteksi ketidakcocokan file, bukan tanda tangan kriptografis dari penerbit.

Pengulangan training dapat mempunyai sedikit perbedaan numerik lintas platform; perbandingan skor tidak perlu menganggap seluruh byte artefak identik. Setelah retraining, jalankan tests dan commit artefak, manifest, reports, dan notebook secara bersama.

Training mengeluarkan warning konvergensi sebagai error. Tidak ada global `warnings.filterwarnings('ignore')`.

Hentikan lalu jalankan ulang Streamlit setelah mengganti artefak atau melakukan retraining agar cache model dan laporan tidak mencampur dua versi.

## Pemeriksaan sebelum dan setelah build

Jalankan `python scripts/verify_package.py --read-only` sebelum membangun ulang. Perintah memeriksa paket yang ada, termasuk hash sumber, model/data, notebook, prediksi, metrik, threshold, dan seluruh tes. Jika modul inti berubah, bangun ulang bundle melalui `build_notebook.py`; jangan mengedit checksum manifest untuk melewati pemeriksaan.

CI menyimpan snapshot commit sebelum build. Setelah `build_notebook.py` dan `build_docs.py`, `compare_reproduction.py --reference PATH_SNAPSHOT` membandingkan metrik JSON, sembilan tabel CSV, sumber sel notebook, serta dokumen hasil generator. Toleransi JSON: rtol 1e-9 / atol 1e-12; tabel: rtol 1e-7 / atol 1e-9. Perbedaan di luar toleransi menggagalkan CI dan harus ditinjau, bukan ditutup dengan mengganti referensi otomatis.

Durasi training, byte serialisasi model, versi patch runtime, byte output notebook/figur, dan waktu verifikasi tidak dibandingkan untuk kesamaan reproduksi. Checksum model setiap bundle tetap diperiksa secara terpisah, dan prediksinya harus sesuai laporan. Aturan ini menguji konsistensi numerik; bukan audit keamanan atau bukti bahwa semua gambar identik. Lihat [workflow](../.github/workflows/README.md).

## Scope aplikasi

`student_success/schema.py` dipakai oleh training, form, dan batch. `student_success/inference.py` menangani pemuatan artefak, probabilitas, kategori tindakan, dan rekomendasi. Input tambahan di CSV tidak dipakai sebagai fitur dan tidak diekspor; `source_row` menjaga urutan. Batch bersifat all-or-nothing agar baris invalid tidak hilang diam-diam.
