# Codespaces — lingkungan pengembangan

[README utama](../README.md) · [Peta repository](../docs/REPOSITORY_GUIDE.md)

`devcontainer.json` memakai image Python **3.12**, sesuai metadata paket dan CI. Setelah container dibuat, setup memasang `requirements-notebook.txt` menggunakan interpreter yang sama, lalu menjalankan `pip check`. Rangkaian `&&` menghentikan setup ketika langkah sebelumnya gagal.

Ketika editor terhubung, aplikasi dijalankan melalui `python -m streamlit run app.py`; port 8501 dibuka sebagai preview. Proteksi CORS dan XSRF tetap mengikuti bawaan Streamlit. Tidak ada dependency sistem tambahan yang diperlukan.

Setelah memperbarui konfigurasi, gunakan **Codespaces: Rebuild Container**, lalu periksa:

```bash
python --version
python -m pip check
python scripts/check_release.py
```

Python harus 3.12. Jika server sudah berjalan, gunakan preview port 8501; jangan memulai instance kedua pada port yang sama. Jika proses server berhenti, jalankan kembali `python -m streamlit run app.py` dari root.

Konfigurasi telah diperiksa secara statis; keberhasilan build Codespaces aktual dicatat terpisah dari tes lokal dan CI.
