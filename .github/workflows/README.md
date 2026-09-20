# Workflows — Project quality

[Kembali ke README utama](../../README.md) · [Peta repository](../../docs/REPOSITORY_GUIDE.md)

Workflow adalah urutan perintah yang dijalankan oleh GitHub Actions pada lingkungan sementara.

## Isi folder

| File atau folder | Fungsi | Kapan dibuka |
|---|---|---|
| [quality.yml](quality.yml) | CI Python 3.12: memeriksa paket commit, lalu mereproduksi dan membandingkan eksperimen. | Memeriksa pemicu, lingkungan, atau tahapan otomatisasi. |


## Pemicu dan alur

Workflow berjalan pada push ke `main`, push tag `v*`, pull request menuju `main`, atau pemicu manual. Kedua job memakai Ubuntu dan Python 3.12 dengan izin `contents: read`.

1. **Check committed package (`release-package`)** memasang dependensi, menjalankan `pip check`, lalu `verify_package.py --read-only` terhadap file checkout. Pemeriksaan mencakup integritas model/data/kode, schema, notebook, laporan prediksi dan metrik, threshold, serta seluruh tests. Tes yang dilewati menggagalkan job. `git diff --exit-code` memastikan file terlacak tidak berubah.
2. **Reproduce the experiment (`reproduction`)** hanya berjalan setelah job pertama berhasil. Job ini menyimpan snapshot commit melalui `git archive`, membangun notebook dan dokumen, memeriksa integritas hasil, membandingkannya dengan snapshot, lalu menjalankan verifier kembali.

Perbandingan numerik memakai toleransi terdokumentasi. Waktu training, byte model/figur/output notebook, versi patch runtime, dan timestamp bukan syarat identik; checksum tiap model dan kesesuaian probabilitas tetap diperiksa. Lihat [batas reproduksi](../../docs/REPRODUCIBILITY.md).

Keluaran training dan perubahan dokumen pada runner bersifat sementara. Workflow ini **tidak melakukan commit/push, mengunggah artefak hasil run, atau deployment**. Karena itu metrik baru pada runner tidak otomatis mengganti laporan yang tersimpan di repository.

Jika gagal, buka langkah merah di Actions dan baca error pertama yang relevan. Cakupan dan bukti run terdahulu ada di [README tests](../../tests/README.md).

Sumber konfigurasi: [GitHub Actions — workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).
