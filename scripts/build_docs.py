"""Refresh metric-driven documentation after training (does not retrain)."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from student_success.schema import FIELDS
m=json.loads((ROOT/'reports/metrics.json').read_text());manifest=json.loads((ROOT/'artifacts/manifest.json').read_text())
h=m['historical_holdout'];p=h['policy'];ci=m['bootstrap_95ci']
def write(path,text):(ROOT/path).write_text(text.strip()+'\n',encoding='utf-8')

# Preserve the hand-written README and refresh only its metric block.
readme_path=ROOT/'README.md'
readme=readme_path.read_text(encoding='utf-8')
start_marker='<!-- MODEL_RESULTS:START -->'
end_marker='<!-- MODEL_RESULTS:END -->'
if readme.count(start_marker)!=1 or readme.count(end_marker)!=1:
    raise ValueError('README must contain exactly one MODEL_RESULTS start/end marker pair.')
start=readme.index(start_marker)+len(start_marker)
end=readme.index(end_marker)
if start>=end:
    raise ValueError('README MODEL_RESULTS markers are out of order.')
results=f'''Model terpilih: **{m['selected_candidate']}**, dengan kalibrasi sigmoid dan threshold peninjauan **{m['threshold']:.2f}**. Angka berikut berasal dari **{m['counts']['historical_holdout']:,} baris holdout historis**; rincian tersedia di [model card](docs/MODEL_CARD.md) dan [metrics.json](reports/metrics.json).

| Ukuran | Hasil | Arti praktis |
|---|---:|---|
| Accuracy tiga kelas | {h['accuracy']:.2%} | Bagian status yang diprediksi benar |
| Macro F1 | {h['macro_f1']:.4f} | Rata-rata F1 dengan bobot sama untuk ketiga kelas |
| Weighted F1 | {h['weighted_f1']:.4f} | F1 dengan bobot sesuai jumlah contoh setiap kelas |
| Recall kebijakan Dropout | {p['recall']:.2%} | Bagian kasus Dropout aktual yang ditandai |
| Precision kebijakan Dropout | {p['precision']:.2%} | Bagian profil yang ditandai dan memang berstatus Dropout |
| Review rate | {p['review_rate']:.2%} | Bagian seluruh profil yang membutuhkan peninjauan |
| Dropout average precision | {h['dropout_average_precision']:.4f} | Ringkasan hubungan precision dan recall di berbagai ambang |

Pada ambang ini, **{p['tp']} dari {p['tp']+p['fn']} kasus Dropout** teridentifikasi dan **{p['fn']} kasus** terlewat. Ada **{p['fp']} profil selain Dropout** yang juga ditandai, sehingga total **{p['review_count']} profil** perlu ditinjau. Recall tinggi disertai beban kerja yang besar; kapasitas tim nyata belum ditetapkan.

**Holdout ini pernah dilihat pada submission lama.** Angka tersebut bukan validasi eksternal independen dan tidak dibandingkan langsung sebagai peningkatan atas model lama yang menggunakan fitur semester 2 serta finansial.'''
readme_path.write_text(readme[:start]+'\n'+results.strip()+'\n'+readme[end:],encoding='utf-8')

per_class='\n'.join(f"| {c} | {h['classification_report'][c]['precision']:.3f} | {h['classification_report'][c]['recall']:.3f} | {h['classification_report'][c]['f1-score']:.3f} | {h['classification_report'][c]['support']:.0f} |" for c in ['Dropout','Enrolled','Graduate'])
write('docs/MODEL_CARD.md',f'''
# Model card — semester1-v1.0.0

## Intended use

Demonstrasi pendampingan akademik berdasarkan informasi sampai akhir semester 1. Model memprediksi status pada akhir durasi normal program, bukan waktu dropout. Tidak untuk sanksi, penolakan, atau keputusan akademik otomatis.

## Model dan protokol

- Terpilih: `{m['selected_candidate']}` dari kandidat Logistic Regression, Random Forest, HistGradientBoosting.
- Baseline: DummyClassifier prior; seluruh kandidat dibandingkan pada development 5-fold CV.
- Preprocessing: StandardScaler numerik + OneHotEncoder nominal, selalu di dalam pipeline training.
- Kalibrasi: sigmoid 3-fold, ensemble tiga model.
- Fitur: 14; target tiga kelas string; tidak memakai encoder target terpisah.
- Split: 2.654 development, 885 policy validation, 885 historical holdout.
- Threshold: **{m['threshold']:.2f}**, dipilih dengan F2 pada policy validation. Tie memilih threshold lebih tinggi.
- Tidak dilakukan refit pada seluruh data setelah holdout. Artefak sama dengan yang dievaluasi.

Pemilihan model memakai macro F1; kandidat lain dapat memiliki Brier/AP lebih baik. Prosedur tidak memilih ulang model menggunakan hasil holdout.

## Hasil holdout historis

| Kelas | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
{per_class}

Macro F1 **{h['macro_f1']:.4f}**, accuracy **{h['accuracy']:.2%}**, weighted F1 **{h['weighted_f1']:.4f}**. Dropout Brier **{h['dropout_brier']:.4f}**, average precision **{h['dropout_average_precision']:.4f}**.

Kebijakan peninjauan: recall **{p['recall']:.2%}**, precision **{p['precision']:.2%}**, review rate **{p['review_rate']:.2%}**. TP={p['tp']}, FN={p['fn']}, FP={p['fp']}, TN={p['tn']}. Performa ini berbeda dari confusion matrix argmax multiclass.

## Interval 95% bootstrap

| Ukuran | Batas bawah | Batas atas |
|---|---:|---:|
| Macro F1 | {ci['macro_f1']['lower']:.4f} | {ci['macro_f1']['upper']:.4f} |
| Recall kebijakan | {ci['dropout_recall_policy']['lower']:.4f} | {ci['dropout_recall_policy']['upper']:.4f} |
| Precision kebijakan | {ci['dropout_precision_policy']['lower']:.4f} | {ci['dropout_precision_policy']['upper']:.4f} |

500 resampling baris untuk model tetap. Tidak mencakup variasi training/seleksi atau pergeseran distribusi. Jangan menafsirkan interval sebagai jaminan pada institusi baru.

## Error kelompok

Hasil di `reports/subgroup_metrics.csv` mengukur gender, usia, dan status beasiswa hanya untuk diagnosis. Misalnya, kelompok penerima beasiswa dalam holdout memiliki hanya 19 kejadian Dropout; recall lebih tidak stabil. Gender/beasiswa tidak masuk fitur utama, tetapi error kelompok tetap berbeda. Tidak ada klaim fairness atau mitigasi bias yang sudah terbukti.

## Keterbatasan utama

1. Holdout telah diperiksa pada proyek lama; bukan validation eksternal yang pristine.
2. Tidak ada tanggal kejadian; sebagian mahasiswa mungkin sudah dropout sebelum akhir semester 1.
3. Enrolled belum outcome akhir yang tuntas; recall kelas ini terbatas.
4. Data Portugal tidak otomatis sesuai konteks Indonesia.
5. Review rate sekitar setengah data dapat melampaui kapasitas tim; tidak ada kapasitas nyata yang ditetapkan.
6. Kalibrasi dinilai secara internal; probabilitas tetap dapat meleset pada populasi baru.
7. Permutation importance global bukan efek kausal atau penjelasan individual.
8. Tidak ada bukti dampak intervensi atau manfaat operasional nyata.

## Reproduksi dan pembaruan

Manifest mencatat checksum model/data, daftar fitur, threshold, versi library, dan code hashes. Untuk pembaruan, tetapkan protokol baru sebelum eksperimen, dokumentasikan perubahan, dan evaluasi data baru bila tersedia. Jangan memindahkan threshold berdasarkan hasil holdout lama untuk mempercantik skor.
''')

lines=['# Kamus fitur utama','', 'Sumber kategori: UCI dataset 697 / kamus Dicoding. Urutan di bawah adalah urutan input model.', '', '| Feature | Label | Tipe | Domain | Keterangan |','|---|---|---|---|---|']
for key,v in FIELDS.items():
    domain='Kategori: '+', '.join(str(k) for k in v.options) if v.options else f'{v.low}–{v.high}'
    lines.append(f'| `{key}` | {v.label} | {v.kind} | {domain} | {v.description} |')
for key,v in FIELDS.items():
    if v.options:
        lines.extend(['',f'## {v.label}','','| Kode | Arti |','|---|---|'])
        lines.extend(f'| {k} | {value} |' for k,value in v.options.items())
lines.extend(['','## Validasi bersama','','- Harus finite, tidak kosong, dan bertipe numerik yang sesuai.','- Kategori harus ada di kamus; jumlah unit harus bilangan bulat.','- Approved dan without evaluations tidak boleh melebihi enrolled.','- Evaluations boleh melebihi enrolled karena penilaian berulang.','- Extra columns di CSV tidak digunakan untuk prediksi dan tidak diekspor.','- Batas domain demo tidak ditentukan dari min/max dataset. Nilai yang valid tetapi di luar rentang development diberi peringatan.'])
write('docs/FEATURE_DICTIONARY.md','\n'.join(lines))

write('docs/PORTFOLIO_RELEASE.md',f'''
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

Model terpilih `{m['selected_candidate']}`. Macro F1 holdout historis {h['macro_f1']:.4f}. Pada threshold {m['threshold']:.2f}, recall peninjauan Dropout {p['recall']:.2%}, precision {p['precision']:.2%}, dan review rate {p['review_rate']:.2%}.

Hasil bersifat retrospektif pada holdout yang pernah dilihat dalam proyek lama. Tidak ada klaim validasi eksternal atau keberhasilan intervensi.

## Menjalankan

Gunakan Python 3.12, instal `requirements.txt`, lalu jalankan `streamlit run app.py`. Artefak sudah tersedia; panduan lengkap di README. [Buka demo](https://student-success-prediction-95.streamlit.app/).

## Verifikasi sebelum publikasi release

Lihat [hasil verifikasi lokal](VALIDATION.md) dan [kesiapan release](RELEASE_READINESS.md). Kedua job CI harus berhasil pada commit yang akan ditag. Dokumen ini adalah draf release; publikasi tag/release dilakukan pemilik repository.

Arsip submission tetap pada `dicoding-submission-v1.0.0`.
''')
print('Refreshed README metric block, model card, feature dictionary, and release notes.')
