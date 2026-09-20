# Catatan verifikasi paket

Pemeriksaan lokal terakhir: **2026-09-20T03:36:10.027541+00:00**.

## Hasil yang diperiksa

- **39 tes lulus**, tanpa skip, failure, atau error; termasuk Streamlit AppTest.
- Notebook: 41 sel, 28 sel kode dengan urutan eksekusi lengkap; nbformat dan sintaks valid, tanpa output error tersimpan.
- Hash seluruh modul inti, checksum data/model, schema, protokol, dan rentang training sesuai manifest.
- 1770 baris prediksi policy/holdout sesuai inference model yang disimpan; label, tindakan dan metrik diperiksa kembali.
- 91 kandidat threshold dihitung ulang dari policy validation; pilihan threshold sesuai aturan F2.

## Batas bukti

Verifier tidak menjalankan training, kernel Jupyter, browser, deployment, atau build container. Pemeriksaan notebook membaca output tersimpan. Builder terpisah menjalankan kode notebook melalui Python biasa; hasil reproduksi dicatat di [kesiapan release](RELEASE_READINESS.md).

AppTest tidak menggantikan pengujian unduh/unggah lewat browser, tampilan pada semua ukuran layar, atau validasi institusi eksternal. Keberhasilan lokal ini tidak membuktikan bahwa workflow baru sudah berhasil di GitHub Actions.

## Mengulang

```bash
python -m pip install -r requirements-notebook.txt
python scripts/verify_package.py --read-only
```

Tanpa `--read-only`, perintah memperbarui file ini dan `reports/verification.json`. Mode read-only tidak menulis laporan. Rincian tes ada di [tests](../tests/README.md); alur dua job ada di [workflow](../.github/workflows/README.md).
