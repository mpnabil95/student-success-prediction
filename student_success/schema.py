"""One semantic schema for training, forms, CSV validation, and documentation."""
from dataclasses import dataclass
import io
import numpy as np
import pandas as pd

COURSES = {33:'Biofuel Production Technologies',171:'Animation and Multimedia Design',8014:'Social Service (evening)',9003:'Agronomy',9070:'Communication Design',9085:'Veterinary Nursing',9119:'Informatics Engineering',9130:'Equinculture',9147:'Management',9238:'Social Service',9254:'Tourism',9500:'Nursing',9556:'Oral Hygiene',9670:'Advertising and Marketing Management',9773:'Journalism and Communication',9853:'Basic Education',9991:'Management (evening)'}
APPLICATION_MODES = {1:'1st phase - general',2:'Ordinance 612/93',5:'1st phase - Azores',7:'Holders of other higher courses',10:'Ordinance 854-B/99',15:'International bachelor applicant',16:'1st phase - Madeira',17:'2nd phase - general',18:'3rd phase - general',26:'Ordinance 533-A/99 b2',27:'Ordinance 533-A/99 b3',39:'Over 23 years old',42:'Transfer',43:'Change of course',44:'Technological specialization',51:'Change of institution/course',53:'Short cycle diploma',57:'Change of institution/course - international'}
QUALIFICATIONS = {1:'Secondary education',2:"Higher education - bachelor's degree",3:'Higher education - degree',4:"Higher education - master's",5:'Higher education - doctorate',6:'Attendance in higher education',9:'12th year - not completed',10:'11th year - not completed',12:'Other - 11th year',14:'10th year',15:'10th year - not completed',19:'Basic education 3rd cycle',38:'Basic education 2nd cycle',39:'Technological specialization',40:'Higher education - degree (1st cycle)',42:'Professional higher technical course',43:'Higher education - master (2nd cycle)'}

@dataclass(frozen=True)
class Field:
    label: str
    kind: str
    low: float
    high: float
    default: float
    group: str
    description: str
    options: dict | None = None

FIELDS = {
    'Course': Field('Program studi','category',0,10000,9119,'Pendaftaran','Kode program sesuai sumber Portugal; bukan kode prodi Indonesia.',COURSES),
    'Application_mode': Field('Jalur pendaftaran','category',0,60,1,'Pendaftaran','Kategori jalur masuk menurut kamus data sumber.',APPLICATION_MODES),
    'Application_order': Field('Urutan pilihan','integer',0,9,1,'Pendaftaran','Urutan pilihan program, 0 sampai 9.'),
    'Daytime_evening_attendance': Field('Jadwal kuliah','category',0,1,1,'Pendaftaran','Jadwal yang dipilih saat pendaftaran.',{0:'Malam',1:'Siang'}),
    'Previous_qualification': Field('Pendidikan sebelumnya','category',0,50,1,'Pendaftaran','Kategori kualifikasi sebelum masuk.',QUALIFICATIONS),
    'Previous_qualification_grade': Field('Nilai pendidikan sebelumnya','continuous',0,200,130.0,'Pendaftaran','Skala sumber 0–200; jangan memasukkan IPK 0–4.'),
    'Admission_grade': Field('Nilai penerimaan','continuous',0,200,125.0,'Pendaftaran','Skala sumber 0–200.'),
    'Age_at_enrollment': Field('Usia saat masuk','integer',16,100,20,'Pendaftaran','Batas operasional demo 16–100; rentang historis diperiksa terpisah.'),
    'Curricular_units_1st_sem_credited': Field('Unit yang diakui / transfer','integer',0,60,0,'Semester 1','Jumlah curricular units yang dikreditkan pada semester 1; bukan otomatis SKS.'),
    'Curricular_units_1st_sem_enrolled': Field('Unit yang diambil','integer',0,60,6,'Semester 1','Jumlah curricular units yang didaftarkan pada semester 1.'),
    'Curricular_units_1st_sem_evaluations': Field('Jumlah evaluasi','integer',0,120,8,'Semester 1','Jumlah evaluasi; boleh melebihi unit karena evaluasi berulang.'),
    'Curricular_units_1st_sem_approved': Field('Unit yang lulus','integer',0,60,5,'Semester 1','Jumlah unit yang diselesaikan; tidak boleh melebihi unit yang diambil.'),
    'Curricular_units_1st_sem_grade': Field('Rata-rata nilai semester 1','continuous',0,20,12.0,'Semester 1','Skala sumber 0–20. Nol dapat mencerminkan tidak adanya nilai.'),
    'Curricular_units_1st_sem_without_evaluations': Field('Unit tanpa evaluasi','integer',0,60,0,'Semester 1','Tidak boleh melebihi jumlah unit yang diambil.'),
}
FEATURES = list(FIELDS)
CATEGORICAL = [k for k,v in FIELDS.items() if v.kind == 'category']
NUMERICAL = [k for k in FEATURES if k not in CATEGORICAL]
ADMISSION_FEATURES = [k for k,v in FIELDS.items() if v.group == 'Pendaftaran']

class ValidationError(ValueError):
    def __init__(self, issues):
        self.issues = pd.DataFrame(issues, columns=['row','column','message'])
        super().__init__('Input tidak valid. Periksa rincian baris dan kolom.')

def validate_features(frame: pd.DataFrame) -> pd.DataFrame:
    """All-or-nothing validation. Row numbers are 1-based data rows (header excluded)."""
    issues=[]
    if frame.columns.duplicated().any():
        issues.append((0,'schema','Nama kolom duplikat tidak diperbolehkan.'))
    missing=[c for c in FEATURES if c not in frame]
    issues.extend((0,c,'Kolom wajib tidak ditemukan.') for c in missing)
    if len(frame)==0: issues.append((0,'file','Minimal satu baris data diperlukan.'))
    if len(frame)>10000: issues.append((0,'file','Maksimum 10.000 baris per unggahan.'))
    if issues: raise ValidationError(issues)
    out=frame[FEATURES].copy().reset_index(drop=True)
    for col,spec in FIELDS.items():
        raw=out[col]
        num=pd.to_numeric(raw,errors='coerce')
        finite=np.isfinite(num.to_numpy(dtype=float))
        for i in np.flatnonzero(~finite): issues.append((int(i)+1,col,'Wajib berupa angka finite, tanpa nilai kosong.'))
        domain=finite & ((num<spec.low)|(num>spec.high)).to_numpy()
        for i in np.flatnonzero(domain): issues.append((int(i)+1,col,f'Nilai harus di antara {spec.low} dan {spec.high}.'))
        if spec.kind in ['category','integer']:
            nonint=finite & (num.to_numpy(dtype=float)!=np.floor(num.to_numpy(dtype=float)))
            for i in np.flatnonzero(nonint): issues.append((int(i)+1,col,'Nilai harus bilangan bulat.'))
        if spec.options is not None:
            for i in np.flatnonzero(finite & ~num.isin(spec.options).to_numpy()):
                issues.append((int(i)+1,col,'Kode kategori tidak ada dalam kamus data.'))
        out[col]=num
    enrolled=out['Curricular_units_1st_sem_enrolled']
    for col in ['Curricular_units_1st_sem_approved','Curricular_units_1st_sem_without_evaluations']:
        for i in np.flatnonzero((out[col]>enrolled).to_numpy()):
            issues.append((int(i)+1,col,'Tidak boleh melebihi unit yang diambil.'))
    if issues: raise ValidationError(issues)
    for col,spec in FIELDS.items():
        out[col]=out[col].astype(float if spec.kind=='continuous' else int)
    return out

def parse_csv(content: bytes) -> pd.DataFrame:
    """Parse records without implicit indexes or silently discarded fields."""
    if len(content)>10*1024*1024:
        raise ValidationError([(0,'file','Ukuran maksimum 10 MB.')])
    try: text=content.decode('utf-8-sig')
    except UnicodeDecodeError: raise ValidationError([(0,'file','Gunakan encoding UTF-8.')]) from None
    import csv
    candidates=[]
    for sep in [',',';']:
        try:
            header=next(csv.reader(io.StringIO(text),delimiter=sep,strict=True))
            if len(header)>1:
                candidates.append((sum(c in header for c in FEATURES),sep,header))
        except (csv.Error,StopIteration):
            continue
    if not candidates:
        raise ValidationError([(0,'file','CSV tidak dapat dibaca; gunakan koma atau titik koma.')])
    _,sep,header=max(candidates,key=lambda item:item[0])
    if len(set(header))!=len(header):
        raise ValidationError([(0,'schema','Nama kolom CSV duplikat.')])
    if any(not name.strip() for name in header):
        raise ValidationError([(0,'schema','Nama kolom CSV tidak boleh kosong.')])
    reader=csv.reader(io.StringIO(text),delimiter=sep,strict=True)
    records=[]
    row_number=0
    try:
        next(reader)  # The header was inspected above, using the same delimiter.
        for record in reader:
            if not record:  # Blank physical lines are not student records.
                continue
            row_number+=1
            if row_number>10000:
                raise ValidationError([(row_number,'file','Maksimum 10.000 baris per unggahan.')])
            if len(record)!=len(header):
                raise ValidationError([(row_number,'schema',
                    f'Jumlah field {len(record)} berbeda dari header ({len(header)}). Periksa pemisah dan tanda kutip.')])
            records.append(record)
    except csv.Error:
        raise ValidationError([(row_number+1,'file','Format kutipan CSV tidak valid.')]) from None
    return pd.DataFrame(records,columns=header)

def defaults(name='Contoh umum'):
    row={c:s.default for c,s in FIELDS.items()}
    if name=='Perlu dukungan akademik':
        row.update(Curricular_units_1st_sem_approved=1,Curricular_units_1st_sem_grade=10.0,Curricular_units_1st_sem_without_evaluations=2)
    elif name=='Akademik kuat':
        row.update(Curricular_units_1st_sem_enrolled=7,Curricular_units_1st_sem_evaluations=9,Curricular_units_1st_sem_approved=7,Curricular_units_1st_sem_grade=15.0)
    return validate_features(pd.DataFrame([row])).iloc[0].to_dict()

def schema_records():
    return [{'feature':k,**vars(v)} for k,v in FIELDS.items()]
