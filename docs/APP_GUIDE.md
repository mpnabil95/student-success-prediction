# Panduan aplikasi — dari input sampai interpretasi

[README utama](../README.md) · [Indeks dokumentasi](README.md) · [Template CSV](../examples/README.md)

Aplikasi Student Success memiliki empat halaman yang dapat dipilih melalui sidebar. Jalankan aplikasi menggunakan [petunjuk instalasi](../README.md#menjalankan-project). Pengguna tidak perlu menjalankan training atau membuka file model.

## 1. Gambaran Data

Halaman ini menampilkan data historis sumber, bukan catatan mahasiswa aktif atau hasil unggahan baru.

1. Pilih program studi; pilihan kosong berarti semua program studi.
2. Sesuaikan rentang usia saat masuk.
3. Baca jumlah mahasiswa, jumlah/proporsi setiap status, capaian semester 1, dan proporsi dropout per program studi.
4. Perhatikan jumlah mahasiswa dalam setiap kelompok. Persentase dari kelompok kecil lebih mudah berubah.
5. Gunakan Minimal mahasiswa per program untuk menyaring tabel berdasarkan ukuran kelompok. Filter ini hanya memengaruhi tabel program dan ekspornya, bukan kartu statistik atau grafik di atas.
6. Klik Unduh ringkasan program untuk mengekspor tabel yang terlihat, atau Reset filter untuk mengembalikan program dan usia ke seluruh snapshot.

Persentase status memakai jumlah mahasiswa setelah filter. Proporsi dropout per program memakai jumlah mahasiswa pada program tersebut setelah filter. Filter dashboard tidak melatih ulang model atau mengubah ambang peninjauan.

## 2. Prediksi Individu

1. Pilih contoh sintetis, lalu klik **Terapkan contoh**, atau isi formulir sendiri.
2. Lengkapi tab Pendaftaran dan Semester 1 menggunakan skala serta kategori sumber. Panel hasil berada di samping formulir pada layar lebar.
3. Klik **Lihat hasil peninjauan**.
4. Baca status paling mungkin, probabilitas Dropout, ambang, kategori tindakan, dan saran pendampingan.
5. Bila perlu, klik **Unduh hasil individu** untuk menyimpan `student_prediction.csv`.

Mengubah nilai formulir memerlukan pengiriman ulang melalui tombol prediksi agar hasil diperbarui. Hasil yang masih terlihat adalah snapshot pengiriman terakhir. Menerapkan preset menghapus hasil lama. Input tidak valid setelah submit juga menghapus hasil sebelumnya. Profil yang sudah dikirim dipulihkan saat kembali dari halaman lain. Profil sintetis hanya membantu demonstrasi input, bukan mahasiswa nyata.

### Dua keluaran yang berbeda

- **Status paling mungkin** memilih probabilitas terbesar di antara tiga kelas.
- **Kategori tindakan** membandingkan probabilitas Dropout dengan threshold yang tersimpan pada model.

Sebagai ilustrasi dengan threshold 0,19: Graduate 0,55, Dropout 0,25, Enrolled 0,20 berarti prediksi status **Graduate**, tetapi tindakan **Perlu peninjauan**. Ini konsisten karena tujuan tindakan adalah menangkap risiko yang patut ditinjau, meskipun Dropout bukan kelas paling mungkin.

“Pemantauan rutin” tidak berarti bebas risiko. Saran pendampingan berasal dari aturan yang dapat dibaca pada kode inference, bukan bukti penyebab atau jaminan manfaat intervensi.

## 3. Prediksi Batch

Gunakan untuk beberapa profil sekaligus. Pilihan Contoh sintetis memungkinkan percobaan tiga profil tanpa mengunggah file; pilih Unggah CSV untuk memakai file sendiri. Mengganti sumber atau isi file akan menghapus hasil sebelumnya.

1. Unduh template pada halaman aplikasi atau gunakan [students_template.csv](../examples/students_template.csv).
2. Buat salinan untuk inputmu; pertahankan 14 nama kolom pada template.
3. Simpan dalam CSV UTF-8 dengan pemisah koma atau titik koma. Gunakan titik untuk desimal.
4. Unggah file, lalu klik **Validasi dan prediksi**.
5. Jika ada error, perbaiki seluruh baris yang disebutkan dan unggah ulang.
6. Jika berhasil, baca jumlah profil yang perlu ditinjau. Tabel dapat difilter berdasarkan tindakan dan selalu diurutkan dari peluang Dropout tertinggi; nomor source_row tetap mengacu pada input.
7. **Unduh seluruh hasil** menyimpan `batch_predictions.csv` dalam urutan input. **Unduh tampilan terfilter** menyimpan `batch_predictions_filtered.csv` sesuai filter dan urutan tabel. Tombol kedua nonaktif bila tidak ada profil dalam filter.

Batas: **10 MB dan 10.000 baris data**. Semua baris harus valid; aplikasi tidak diam-diam melewatkan baris yang salah. Nama kolom ganda, kolom wajib hilang, nilai kosong, kategori tidak dikenal, dan relasi akademik tidak sah dapat menyebabkan penolakan.

Setiap baris harus memiliki jumlah kolom yang sama dengan header. Kolom berlebih tanpa nama header, kolom yang kurang, header kosong, dan tanda kutip tidak lengkap ditolak sebelum prediksi. Nilai yang memuat pemisah atau baris baru harus diapit tanda kutip CSV. Baris fisik kosong diabaikan; baris yang berisi pemisah dengan nilai kosong tetap divalidasi dan ditolak bila fitur wajib kosong.

Nomor baris pada error dan `source_row` menghitung record data mulai dari 1, tanpa header dan tanpa baris fisik kosong. Satu nilai dalam tanda kutip dapat memuat baris baru, sehingga nomor ini tidak selalu sama dengan nomor baris editor teks. Kolom tambahan hanya diperbolehkan jika mempunyai nama header dan jumlah field setiap record tetap sesuai.

### Aturan input yang sering membingungkan

| Masukan | Cara mengisinya |
|---|---|
| Program studi/jalur masuk/kualifikasi | Form memakai label; CSV memakai kode numerik sesuai kamus fitur |
| Nilai masuk dan kualifikasi sebelumnya | Skala sumber 0–200 |
| Nilai semester | Skala sumber 0–20 |
| Jumlah unit | Bilangan bulat; unit kurikulum bukan otomatis SKS Indonesia |
| Unit lulus atau tanpa evaluasi | Masing-masing tidak boleh melebihi unit yang terdaftar |
| Jumlah evaluasi | Boleh lebih besar dari unit terdaftar karena dapat ada evaluasi berulang |
| Kolom ekstra | Diabaikan saat prediksi dan tidak dimasukkan kembali ke unduhan |
| `Status` | Tidak diperlukan untuk input prediksi |

Domain lengkap berada di [FEATURE_DICTIONARY.md](FEATURE_DICTIONARY.md). Nilai dalam domain yang valid tetapi berada di luar rentang development dapat menghasilkan peringatan; itu berbeda dari error validasi yang menghentikan prediksi.

### Isi unduhan individu dan batch

Keduanya memuat 14 fitur tervalidasi beserta kolom berikut:

| Kolom | Arti |
|---|---|
| `source_row` | Nomor baris input mulai dari 1, tanpa menghitung header; individu selalu 1 |
| `predicted_status` | Dropout, Enrolled, atau Graduate dengan probabilitas tertinggi |
| `prob_dropout` | Perkiraan probabilitas Dropout, dalam rentang 0–1 |
| `prob_enrolled` | Perkiraan probabilitas Enrolled, dalam rentang 0–1 |
| `prob_graduate` | Perkiraan probabilitas Graduate, dalam rentang 0–1 |
| `action` | Perlu peninjauan atau Pemantauan rutin berdasarkan ambang model |
| `model_version` | Identitas versi model yang menghasilkan prediksi |

Ketiga probabilitas berjumlah sekitar 1, dengan toleransi pembulatan. File evaluasi di `reports/` memiliki struktur berbeda karena juga menyimpan label aktual untuk perbandingan; jangan menyamakannya dengan unduhan aplikasi.

Unggahan tidak disimpan sebagai file di repository oleh aplikasi. Identitas pada kolom ekstra tidak ikut diekspor; bila dibutuhkan, pengguna harus menjaga pemetaan lokal melalui `source_row`. Gunakan profil sintetis untuk demo publik.

## 4. Kinerja Model

Halaman ini memiliki tab Hasil evaluasi, Pemilihan model, Diagnostik, dan Batas penggunaan. Grafik interaktif menampilkan tooltip saat diarahkan dengan pointer. Halaman menunjukkan metrik evaluasi dan grafik dari eksperimen yang disertakan. Nilainya tidak dihitung ulang dari file batch yang diunggah.

- **Accuracy/macro F1** menilai prediksi tiga kelas.
- **Recall/precision peninjauan** menilai keputusan menandai berdasarkan probabilitas Dropout.
- **Review rate** menunjukkan beban peninjauan jika ambang tersebut diterapkan pada data evaluasi.

Baca [MODEL_CARD.md](MODEL_CARD.md) untuk metrik per kelas, interval ketidakpastian, dan kelemahan model. Lihat [panduan grafik](../reports/figures/README.md) untuk interpretasi visual.

## Kendala umum

| Gejala | Yang perlu diperiksa |
|---|---|
| Python/Streamlit tidak ditemukan | Gunakan interpreter `.venv` dan pasang requirements dari root repository |
| Versi scikit-learn tidak cocok | Instal versi persis dari requirements; model tersimpan tidak dijamin kompatibel lintas versi |
| Checksum atau schema model berbeda | Pulihkan satu set artefak yang konsisten; jangan mengedit checksum untuk melewati pemeriksaan |
| CSV menjadi satu kolom atau gagal dibaca | Periksa UTF-8, pemisah koma/titik koma, dan nama header template |
| Baris ditolak | Ikuti rincian baris/kolom; gunakan data yang benar, jangan menebak nilai agar lolos |
| Peringatan di luar rentang development | Input mungkin valid secara schema tetapi kurang terwakili dalam data training |
| Model/laporan baru belum terlihat | Hentikan dan mulai ulang aplikasi agar cache diperbarui |

## Batas penggunaan

Hasil bersifat retrospektif, menggunakan data pendidikan Portugal, dan belum tervalidasi pada institusi lain. Tidak ada tanggal dropout per mahasiswa. Gunakan hasil untuk diskusi pendampingan yang dikonfirmasi manusia, bukan sanksi, penolakan beasiswa, atau keputusan administratif otomatis.
