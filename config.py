# =========================
# KONFIGURASI SPREADSHEET
# =========================

# ID Spreadsheet Google Sheets
SPREADSHEET_ID = "1vfDsjo4QxFVasFWc9EhcSmLGRkwy9xu572nGGGGR1SE"

# Nama Sheet
SHEET_AKUN = "akun"
SHEET_DATA_MAGANG = "Data Magang Aktif"
SHEET_DOKUMEN = "Dokumen"

# =========================
# KONFIGURASI KOLOM SHEET AKUN
# =========================
AKUN_COLUMNS = {
    'USERNAME': 'username',
    'PASSWORD': 'password',
    'NAMA_LENGKAP': 'nama_lengkap',  # opsional
    'ROLE': 'role'  # opsional: admin/user
}

# =========================
# KONFIGURASI KOLOM SHEET DATA MAGANG AKTIF
# =========================
DATA_MAGANG_COLUMNS = {
    'ID_PENDAFTAR': 'ID_Pendaftar',
    'WAKTU_DAFTAR': 'Waktu Daftar',
    'NAMA': 'Nama',
    'JENIS_KELAMIN': 'Jenis Kelamin',
    'JURUSAN': 'Jurusan',
    'SEKOLAH': 'Sekolah/Universitas',
    'NIM': 'NIM/NIS',
    'DEPARTEMEN': 'Bagian/Dept',
    'TGL_MULAI': 'Mulai',
    'TGL_AKHIR': 'Akhir',
    'DURASI': 'Bulan',
    'JENJANG': 'Jenjang',
    'STATUS': 'Status',
    'NO_HP': 'Nomer HP',
    'EMAIL': 'Email'
}

# =========================
# KONFIGURASI KOLOM SHEET DOKUMEN
# =========================
DOKUMEN_COLUMNS = {
    'ID_PENDAFTAR': 'ID_Pendaftar',
    'CV': 'CV',
    'TRANSKRIP': 'Transkrip',
    'PROPOSAL': 'Proposal',
    'SURAT_PENGANTAR': 'Surat_Pengantar',
    'STATUS_VERIFIKASI': 'Status_Verifikasi',
    'WAKTU_UPLOAD': 'Waktu_Upload'
}

# =========================
# KONFIGURASI DEPARTEMEN
# =========================
DEPARTEMEN = {
    "HRD": {
        "nama": "HRD",
        "icon": "fa-users",
        "kuota": 5,
        "deskripsi": "Human Resources Development"
    },
    "Finance": {
        "nama": "Finance",
        "icon": "fa-chart-pie",
        "kuota": 3,
        "deskripsi": "Keuangan & Akuntansi"
    },
    "IT": {
        "nama": "IT",
        "icon": "fa-laptop-code",
        "kuota": 4,
        "deskripsi": "Information Technology"
    },
    "Marketing": {
        "nama": "Marketing",
        "icon": "fa-bullhorn",
        "kuota": 4,
        "deskripsi": "Pemasaran & Komunikasi"
    },
    "Production": {
        "nama": "Production",
        "icon": "fa-industry",
        "kuota": 6,
        "deskripsi": "Produksi & Operasional"
    }
}

# =========================
# KONFIGURASI APLIKASI
# =========================
APP_CONFIG = {
    'nama_aplikasi': 'JAPFA Internship Program',
    'perusahaan': 'PT Japfa Comfeed Indonesia Tbk',
    'lokasi': 'Sidoarjo',
    'version': '1.0.0'
}

# =========================
# PESAN-PESAN APLIKASI
# =========================
MESSAGES = {
    'login_success': '✅ Login berhasil! Mengalihkan...',
    'login_failed': '❌ Username atau password salah!',
    'field_required': '❌ Semua field wajib harus diisi!',
    'agreement_required': '❌ Harap setujui semua pernyataan untuk melanjutkan!',
    'save_success': '✅ Data berhasil disimpan!',
    'save_failed': '❌ Gagal menyimpan data!',
    'doc_complete': '✅ Selamat! Semua dokumen Anda sudah lengkap dan terverifikasi!',
    'doc_incomplete': '⚠️ Dokumen Belum Lengkap',
    'reg_not_found': '❌ Nomor registrasi tidak ditemukan.'
}

departemen_list = [
    "IT",
    "HRD",
    "Finance",
    "Produksi",
    "Quality Control",
    "Marketing"
]

jenissekolah_list = ["Sekolah", "Universitas"]

periode_list = ["Semester I", "Semester II", "Semester III"]

bulan_map = {
    "Januari": "01",
    "Februari": "02",
    "Maret": "03",
    "April": "04",
    "Mei": "05",
    "Juni": "06",
    "Juli": "07",
    "Agustus": "08",
    "September": "09",
    "Oktober": "10",
    "November": "11",
    "Desember": "12"
}

nama_kolom_data_absen = [
    "ID_Magang",
    "Nama",
    "Tanggal",
    "Jam Masuk",
    "Jam Pulang",
    "Scan Masuk",
    "Scan Keluar",
    "Terlambat",
    "Plg Cpt",
    "Lembur",
    "Jam Kerja",
    "Jml Hadir"
    ]

BULAN_INDONESIA = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
    'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
}