# GitHub — otomatisasi repository

[Kembali ke README utama](../README.md) · [Peta repository](../docs/REPOSITORY_GUIDE.md)

Folder ini berisi konfigurasi khusus GitHub. Otomatisasi menjalankan pemeriksaan ketika kode diperbarui sehingga hasilnya dapat diperiksa melalui tab Actions.

Workflow memiliki dua job berurutan: **Check committed package** memeriksa file yang akan dikirim, lalu **Reproduce the experiment** membangun ulang dan membandingkan hasil dengan snapshot commit. Keduanya perlu berhasil sebelum release.

## Isi folder

| File atau folder | Fungsi | Kapan dibuka |
|---|---|---|
| [workflows/](workflows/README.md) | Definisi workflow Project quality. | Memahami kapan dan bagaimana GitHub menguji project. |


## Untuk pembaca umum

Buka [Actions](https://github.com/mpnabil95/student-success-prediction/actions) untuk melihat hasil. Tanda berhasil berarti langkah workflow pada commit tersebut selesai; baca [cakupan tes](../tests/README.md) untuk mengetahui batas pemeriksaannya.

Tidak ada workflow deployment pada versi ini. Memperbarui konfigurasi di folder ini tidak melatih model yang sedang berjalan pada layanan eksternal atau menerbitkan release secara otomatis.

## Mengapa file ini bernama GUIDE.md?

GitHub memprioritaskan README yang berada langsung di `.github/` atas README root untuk beranda repository. Panduan ini menggunakan nama `GUIDE.md` agar beranda menampilkan README utama. Tetap gunakan [README workflow](workflows/README.md) untuk rincian otomatisasi; subfolder tersebut tidak termasuk lokasi prioritas README beranda.

Sumber: [GitHub Docs — About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes).
