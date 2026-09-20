# Tests — apa yang diperiksa otomatis

[Kembali ke README utama](../README.md) · [Peta repository](../docs/REPOSITORY_GUIDE.md)

Tes otomatis memeriksa perilaku tertentu dengan input yang hasilnya dapat diperiksa. Tes membantu menemukan regresi, tetapi tidak membuktikan bahwa prediksi akan berhasil di semua kampus atau bahwa seluruh interaksi browser sudah diuji.

## Isi folder

| File atau folder | Fungsi | Kapan dibuka |
|---|---|---|
| [test_contracts.py](test_contracts.py) | 15 tes data/artefak: input invalid, domain, relasi akademik, CSV, preset, threshold, split, dan konsistensi inference. | Memeriksa aturan inti atau menambahkan tes untuk perubahan perilaku model/input. |
| [test_streamlit.py](test_streamlit.py) | 10 tes AppTest: navigasi, filter, input/state individu dan batch, serta rendering evaluasi. | Memeriksa alur aplikasi dan spesifikasi grafik. |
| [test_ui_assets.py](test_ui_assets.py) | 5 tes aset ikon, fallback ikon internal, CSS, dan tema. | Mencegah regresi aset tampilan. |
| [test_csv_structure.py](test_csv_structure.py) | 6 tes struktur CSV, delimiter, kutipan, batas ukuran/baris, serta kolom kurang/berlebih. | Mencegah pergeseran kolom dan hilangnya nilai secara diam-diam. |
| [test_release_checks.py](test_release_checks.py) | 3 tes yang merusak salinan metrik, probabilitas, atau notebook dan memastikan gate menolak paket. | Memastikan artefak bermasalah terdeteksi sebelum build. |


## Menjalankan

Dari root repository, dengan environment aktif:

```bash
python -m pip install -r requirements-notebook.txt
python -m unittest discover -s tests -v
python scripts/verify_package.py --read-only
```

Di Windows tanpa aktivasi, gunakan `.\.venv\Scripts\python.exe` sebagai pengganti `python`. Gunakan dependensi notebook untuk seluruh suite. Verifier mewajibkan Streamlit/nbformat, memeriksa integritas paket, dan gagal jika ada tes dilewati. Suite saat perbaikan audit berjumlah **39 tes**, seluruhnya lulus; bukti lokal bertanggal tersedia di [VALIDATION.md](../docs/VALIDATION.md).

## Bukti CI historis

[Project quality — run 34809204916](https://github.com/mpnabil95/student-success-prediction/actions/runs/34809204916), commit `6a5c888dea0b6719f248ed0454c61ee6da68c5d6`, diperiksa pada 14 September 2026:

| Pemeriksaan | Bukti |
|---|---|
| Instalasi dependensi notebook dan import Streamlit/nbformat | Langkah workflow berhasil |
| Pembangunan dan eksekusi notebook melalui builder | Langkah workflow berhasil |
| Pembangunan dokumen | Langkah workflow berhasil |
| Unit/integration tests | Log menunjukkan 16 tes, OK; AppTest dijalankan dan tidak dilewati |
| Validasi struktur notebook dengan nbformat | Langkah workflow berhasil |

Bukti di atas berlaku untuk commit tersebut. Audit berikutnya juga memeriksa keberhasilan [run 35210959197](https://github.com/mpnabil95/student-success-prediction/actions/runs/35210959197) pada baseline `0fa0c24e508f0221a2dae8044da17c3d7317e2bc`. Workflow dua job pada paket ini belum dijalankan di GitHub sebelum pemilik melakukan commit. Status terbaru dapat diperiksa di [Actions](https://github.com/mpnabil95/student-success-prediction/actions). `reports/verification.json` merekam pemeriksaan lokal bertanggal; CI menggunakan mode read-only dan tidak memperbarui file tersebut.

## Yang belum dicakup

Tes AppTest memeriksa batch sintetis dan perubahan state, tetapi belum menguji pemilih file unggahan dan unduhan dari browser sesungguhnya, tata letak pada berbagai ukuran layar, atau deployment publik. Builder menjalankan kode notebook melalui Python; validasi nbformat memeriksa format dan bukan eksekusi ulang melalui kernel Jupyter terpisah. CI juga belum menjalankan audit kerentanan dependensi.

[Workflow](../.github/workflows/README.md) · [Catatan paket awal](../docs/VALIDATION.md) · [Batas model](../docs/MODEL_CARD.md)

## Verifikasi pembaruan antarmuka

Pada 14 September 2026, suite lokal terdiri dari **23 tes: 15 kontrak data/model dan 8 tes antarmuka**. Seluruhnya lulus tanpa skip. Keberhasilan CI 16 tes pada bagian historis tetap berlaku untuk commit lamanya; perubahan antarmuka ini perlu melewati CI lagi setelah di-commit. [Catatan UI](../docs/UI_CHANGELOG.md) memuat cakupan dan batas verifikasi.
