# Scripts — perintah bantuan dan file yang berubah

[Kembali ke README utama](../README.md) · [Peta repository](../docs/REPOSITORY_GUIDE.md)

Folder ini menyediakan perintah untuk membangun dokumen dan memeriksa hasil. Jalankan dari root repository dengan environment Python 3.12 project. Pengguna yang hanya ingin mencoba aplikasi tidak perlu menjalankan scripts ini.

## Isi folder

| File atau folder | Fungsi | Kapan dibuka |
|---|---|---|
| [build_notebook.py](build_notebook.py) | Membangun dan mengeksekusi notebook, termasuk menjalankan kembali training. | Mengulang eksperimen lengkap dan menghasilkan notebook dengan output baru. |
| [build_docs.py](build_docs.py) | Menyegarkan blok hasil README, model card, kamus fitur, dan draf release dari hasil yang tersedia. | Setelah eksperimen berubah atau template dokumentasi diperbaiki. |
| [verify_package.py](verify_package.py) | Memeriksa sintaks, keluaran notebook, tests, dan hash kode; menyimpan hasil verifikasi lokal. | Memeriksa paket setelah lingkungan dan keluaran siap. |
| [check_release.py](check_release.py) | Memeriksa integritas paket yang ada tanpa training atau penulisan laporan. | Memeriksa checksum, notebook, schema, prediksi, metrik, split, dan threshold. |
| [compare_reproduction.py](compare_reproduction.py) | Membandingkan hasil build dengan snapshot paket referensi. | Membuktikan keluaran eksperimen yang di-commit dapat direproduksi. |


## Dampak setiap perintah

| Perintah dari root | File yang ditulis |
|---|---|
| `python scripts/build_notebook.py` | `notebook.ipynb`; melalui training juga `artifacts/`, laporan eksperimen, `reports/figures/`, dan `examples/students_template.csv` |
| `python scripts/build_docs.py` | Blok hasil pada `README.md`, `docs/MODEL_CARD.md`, `docs/FEATURE_DICTIONARY.md`, `docs/PORTFOLIO_RELEASE.md` |
| `python scripts/verify_package.py` | `reports/verification.json`, `docs/VALIDATION.md` |
| `python scripts/verify_package.py --read-only` | Tidak menulis laporan; integritas dan seluruh tes harus lulus tanpa skip |
| `python scripts/check_release.py` | Tidak menulis file |
| `python scripts/compare_reproduction.py --reference PATH_SNAPSHOT` | Tidak menulis file; membandingkan metrik, tabel, dan dokumen dengan snapshot |

## Urutan untuk mengulang eksperimen lengkap

```bash
python scripts/verify_package.py --read-only
python scripts/build_notebook.py
python scripts/build_docs.py
python scripts/verify_package.py
```

Builder notebook sudah menjalankan training; menjalankan `python -m student_success.train` sebelumnya akan mengulang pekerjaan. Jika hanya menyunting penjelasan Markdown, training tidak diperlukan.

Pemeriksaan pertama memvalidasi keluaran yang sudah tersedia sebelum tertimpa oleh build. Untuk perubahan kode inti yang disengaja, kegagalan hash sebelum build berarti bundle perlu diregenerasi; jangan mengubah checksum secara manual. CI menyimpan referensi commit dan membandingkan reproduksi pada job terpisah. Rincian toleransi tersedia di [REPRODUCIBILITY.md](../docs/REPRODUCIBILITY.md).

## Memelihara dokumentasi

- README utama disunting manual, kecuali bagian di antara penanda `<!-- MODEL_RESULTS:START -->` dan `<!-- MODEL_RESULTS:END -->`.
- `build_docs.py` hanya memperbarui isi di antara kedua penanda tersebut. Pertahankan masing-masing penanda tepat satu kali dan dengan urutan yang benar. Penanda hilang/duplikat menyebabkan script berhenti sebelum menulis dokumen.
- Model card, kamus fitur, dan draf release ditulis ulang sepenuhnya. Untuk perubahan permanen pada ketiganya, sunting template di `build_docs.py`.
- `verify_package.py` menulis catatan lingkungan tempat ia dijalankan. Catatan tersebut berbeda dari riwayat CI di GitHub; bukti run historis tersedia di [README tests](../tests/README.md#bukti-ci-historis).
- README folder, panduan aplikasi, dan peta repository tetap disunting manual.

Setelah regenerasi, periksa diff, termasuk apakah narasi manual, contoh angka, jumlah fitur, dan batas penggunaan masih sesuai eksperimen baru. Mulai ulang aplikasi setelah mengganti model/laporan agar cache tidak mencampur versi.
