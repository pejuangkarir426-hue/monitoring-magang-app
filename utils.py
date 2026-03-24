import streamlit as st
import pandas as pd
import hashlib
import json
import time
from datetime import datetime
from config import SPREADSHEET_ID, SHEET_AKUN, SHEET_DATA_MAGANG, SHEET_DOKUMEN, BULAN_INDONESIA
from config import AKUN_COLUMNS, DATA_MAGANG_COLUMNS, DOKUMEN_COLUMNS, bulan_map
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from google.oauth2.service_account import Credentials
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# FUNGSI KONEKSI GOOGLE SHEETS (SEMUA PAKAI INI)
# =========================

def get_gspread_client():
    """
    Mendapatkan koneksi ke Google Sheets menggunakan secrets dari Streamlit
    """
    try:
        # Baca credentials dari st.secrets
        google_credentials = st.secrets["GOOGLE_CREDENTIALS"]
        
        # Karena st.secrets mengembalikan AttrDict, kita konversi ke dict biasa
        if hasattr(google_credentials, 'to_dict'):  # Untuk AttrDict
            creds_info = google_credentials.to_dict()
        elif isinstance(google_credentials, dict):
            creds_info = google_credentials
        else:
            # Jika dalam bentuk string, parse JSON
            creds_info = json.loads(google_credentials)
        
        # PASTIKAN private_key dalam format yang benar
        if 'private_key' in creds_info:
            # Jika private_key masih dalam format dengan \n, biarkan
            # Jika tidak, pastikan formatnya benar
            if '\\n' in creds_info['private_key']:
                creds_info['private_key'] = creds_info['private_key'].replace('\\n', '\n')
        
        # Buat credentials
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Gagal terhubung ke Google Sheets: {str(e)}")
        return None

def get_spreadsheet():
    """Mendapatkan objek spreadsheet"""
    client = get_gspread_client()
    if client:
        return client.open_by_key(SPREADSHEET_ID)
    return None

def get_worksheet(sheet_name):
    """
    Fungsi untuk mendapatkan worksheet dari Google Sheets
    """
    spreadsheet = get_spreadsheet()
    if spreadsheet:
        return spreadsheet.worksheet(sheet_name)
    return None

# =========================
# FUNGSI CACHING DAN DATA
# =========================

def load_data_for_login(sheetname):
    """
    Fungsi untuk membaca data dari Google Sheets (khusus login)
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return pd.DataFrame()
        
        worksheet = spreadsheet.worksheet(sheetname)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari sheet '{sheetname}': {e}")
        return pd.DataFrame()

@st.cache_data(ttl=None, show_spinner="📊 Memuat data dari Google Sheets...")
def load_data_cached(sheetname):
    """
    Fungsi yang di-cache untuk membaca data dari Google Sheets
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return pd.DataFrame()
        
        worksheet = spreadsheet.worksheet(sheetname)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari sheet '{sheetname}': {e}")
        # Return DataFrame kosong dengan struktur yang sesuai
        if sheetname == "database_magang":
            return pd.DataFrame(columns=['ID_Magang', 'Nama', 'Jenis Kelamin', 'Jurusan/Fakultas', 
                                        'Jenjang', 'Sekolah/Universitas', 'Jenis Univ/Sekolah', 
                                        'Bagian/Dept', 'Sub Dept', 'Bulan', 'Mulai', 'Akhir', 
                                        'Periode', 'Tahun', 'Keterangan', 'Catatan', 'S/A/SB/OP/DT'])
        elif sheetname == "data_presensi":
            return pd.DataFrame(columns=['ID_Magang', 'Tanggal', 'Jam Masuk', 'Jam Pulang', 
                                        'Scan Masuk', 'Scan Keluar', 'Terlambat', 'Status Terbayar'])
        else:
            return pd.DataFrame()

def load_data(sheetname):
    return load_data_cached(sheetname)

def refresh_all_cache():
    """
    Membersihkan semua cache data dan memperbarui session state
    """
    try:
        # Clear semua cache
        st.cache_data.clear()
        
        # Update timestamp di session state
        if 'last_refresh' in st.session_state:
            st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")
        
        # Reload data ke session state jika user sudah login
        if st.session_state.get('logged_in', False):
            with st.spinner("Memperbarui data di session state..."):
                st.session_state.data_magang = load_data_cached("database_magang")
                st.session_state.data_presensi = load_data_cached("data_presensi")
                st.session_state.data_departemen = load_data_cached("departemen")
                st.session_state.data_subdepartemen = load_data_cached("sub_departemen")
        
        st.success("✅ Cache berhasil diperbarui!")
        return True
    except Exception as e:
        st.error(f"Gagal memperbarui cache: {e}")
        return False

def refresh_sheet_cache(sheetname):
    """
    Membersihkan cache untuk sheet tertentu dan memperbarui session state
    """
    try:
        # Clear semua cache (lebih sederhana daripada key-based)
        st.cache_data.clear()
        
        # Update timestamp
        if 'last_refresh' in st.session_state:
            st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")
        
        # Reload sheet tertentu ke session state
        if st.session_state.get('logged_in', False):
            # Mapping sheetname ke session state key
            sheet_to_session = {
                "database_magang": "data_magang",
                "data_presensi": "data_presensi",
                "departemen": "data_departemen",
                "sub_departemen": "data_subdepartemen"
            }
            
            if sheetname in sheet_to_session:
                session_key = sheet_to_session[sheetname]
                st.session_state[session_key] = load_data_cached(sheetname)
                st.success(f"✅ Cache untuk sheet '{sheetname}' berhasil diperbarui!")
            else:
                # Jika sheet tidak dikenal, reload semua
                refresh_all_cache()
        
        return True
    except Exception as e:
        st.error(f"Gagal memperbarui cache untuk sheet '{sheetname}': {e}")
        return False

def refresh_data_in_session():
    """
    Fungsi lengkap untuk memperbarui semua data di cache dan session state
    """
    try:
        # Clear cache yang ada
        st.cache_data.clear()
        
        # Load data untuk semua sheet yang diperlukan
        st.session_state.data_magang = load_data_cached("database_magang")
        st.session_state.data_presensi = load_data_cached("data_presensi")
        st.session_state.data_departemen = load_data_cached("departemen")
        st.session_state.data_subdepartemen = load_data_cached("sub_departemen")
        
        # Update timestamp
        st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")
        
        return True
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return False

# =========================
# FUNGSI AUTHENTIKASI USER
# =========================
def authenticate_user1(username, password):
    """
    Memverifikasi username dan password dari sheet "akun"
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return {
                'success': False, 
                'message': 'Gagal terhubung ke database. Coba lagi nanti.'
            }
        
        # Buka sheet akun
        try:
            worksheet = spreadsheet.worksheet(SHEET_AKUN)
        except:
            # Buat sheet akun jika belum ada
            worksheet = spreadsheet.add_worksheet(title=SHEET_AKUN, rows=100, cols=4)
            worksheet.update('A1', [[
                AKUN_COLUMNS['USERNAME'],
                AKUN_COLUMNS['PASSWORD'],
                AKUN_COLUMNS['NAMA_LENGKAP'],
                AKUN_COLUMNS['ROLE']
            ]])
            # Tambahkan data default
            worksheet.append_row(['admin', hash_password('admin123'), 'Administrator', 'admin'])
            worksheet.append_row(['user', hash_password('user123'), 'Regular User', 'user'])
        
        # Ambil semua data
        data = worksheet.get_all_records()
        
        # Cari username yang cocok
        for row in data:
            if row[AKUN_COLUMNS['USERNAME']].strip().lower() == username.strip().lower():
                stored_password = row[AKUN_COLUMNS['PASSWORD']]
                
                # Verifikasi password
                if verify_password(password, stored_password):
                    return {
                        'success': True,
                        'message': 'Login berhasil',
                        'user_data': {
                            'username': row[AKUN_COLUMNS['USERNAME']],
                            'nama_lengkap': row.get(AKUN_COLUMNS['NAMA_LENGKAP'], username),
                            'role': row.get(AKUN_COLUMNS['ROLE'], 'user')
                        }
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Password salah!'
                    }
        
        return {
            'success': False,
            'message': 'Username tidak ditemukan!'
        }
        
    except Exception as e:
        st.error(f"Error detail: {str(e)}")
        return {
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }

# =========================
# FUNGSI HASH PASSWORD
# =========================
def hash_password(password):
    """Meng-hash password menggunakan SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password, stored_password):
    """Memverifikasi password dengan stored password"""
    if len(stored_password) == 64:
        return hash_password(input_password) == stored_password
    else:
        return input_password == stored_password

# =========================
# FUNGSI MENYIMPAN DATA MAGANG
# =========================
def save_internship_data(form_data):
    """
    Menyimpan data magang baru ke spreadsheet
    """
    try:
        # Ambil data lama untuk cek duplikat
        df = load_data_cached("database_magang")

        # Cek apakah ID sudah ada
        if form_data["id_magang"] in df["ID_Magang"].astype(str).values:
            st.error("❌ ID Magang sudah terdaftar!")
            return False

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False
            
        sheet = spreadsheet.worksheet("database_magang")

        # Susun sesuai urutan kolom spreadsheet
        new_row = [
            form_data["id_magang"],
            form_data["nama"],
            form_data["jenis_kelamin"],
            form_data["jurusan"],
            form_data["jenjang"],
            form_data["sekolah"],
            form_data["jenis_sekolah"],
            form_data["bagian_dept"],
            form_data["sub_dept"],
            form_data["bulan"],
            form_data["tgl_mulai"],
            form_data["tgl_akhir"],
            form_data["periode"],
            form_data["tahun"],
            form_data["keterangan"]
        ]

        # Tambahkan data di baris ke-2
        sheet.insert_row(new_row, index=2)

        return True

    except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")
        return False

def update_internship_data(id_magang, updated_data):
    """
    Fungsi untuk mengupdate data magang di spreadsheet berdasarkan ID_Magang
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False
            
        worksheet = spreadsheet.worksheet("database_magang")
        
        # Ambil semua data termasuk header
        all_data = worksheet.get_all_values()
        
        # Cari baris dengan ID_Magang yang sesuai
        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 0 and row[0] == id_magang:
                
                # Siapkan data untuk kolom A sampai P (16 kolom)
                columns_order = [
                    'ID_Magang', 'Nama', 'Jenis Kelamin', 'Jurusan/Fakultas',
                    'Jenjang', 'Sekolah/Universitas', 'Jenis Univ/Sekolah',
                    'Bagian/Dept', 'Sub Dept', 'Bulan', 'Mulai', 'Akhir',
                    'Periode', 'Tahun', 'Keterangan', 'Catatan'
                ]
                
                row_data = []
                for col in columns_order:
                    if col in updated_data:
                        row_data.append(str(updated_data[col]))
                    else:
                        row_data.append("")
                
                # Update kolom A sampai P
                update_range = f'A{i}:P{i}'
                worksheet.update(update_range, [row_data])
                
                # Kosongkan kolom Q
                worksheet.update(f'Q{i}', [[""]])
                
                return True
        
        st.error(f"ID Magang {id_magang} tidak ditemukan")
        return False
        
    except Exception as e:
        st.error(f"Error saat mengupdate data: {str(e)}")
        return False

def delete_internship_data(id_magang):
    """
    Fungsi untuk menghapus data magang
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
            
        worksheet = spreadsheet.worksheet("database_magang")

        # Ambil semua data
        all_data = worksheet.get_all_values()

        baris_yang_dihapus = []

        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 0 and str(row[0]) == str(id_magang):
                baris_yang_dihapus.append(i)

        if not baris_yang_dihapus:
            return False, f"ID Magang {id_magang} tidak ditemukan"

        # hapus dari bawah
        for baris in sorted(baris_yang_dihapus, reverse=True):
            worksheet.delete_rows(baris)

        return True, f"Data ID {id_magang} berhasil dihapus"

    except Exception as e:
        return False, str(e)

# =========================
# FUNGSI MENYIMPAN DATA PRESENSI
# =========================
def append_to_sheet(sheetname, rows):
    """Menambahkan beberapa baris ke sheet Google Sheets."""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False
            
        worksheet = spreadsheet.worksheet(sheetname)
        worksheet.append_rows(rows)
        return True
    except Exception as e:
        st.error(f"Gagal menambahkan data ke sheet '{sheetname}': {e}")
        return False

def hapus_data_dari_sheets(sheet_name, id_magang, tanggal):
    """
    Fungsi untuk menghapus data dari Google Sheets berdasarkan ID_Magang dan Tanggal
    """
    try:
        worksheet = get_worksheet(sheet_name)
        if not worksheet:
            return
            
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) <= 1:  # Hanya header atau kosong
            st.warning(f"Sheet {sheet_name} kosong atau hanya berisi header")
            return
        
        header = all_values[0]
        
        # Cari indeks kolom
        try:
            idx_id = header.index('ID_Magang')
            idx_tgl = header.index('Tanggal')
        except ValueError as e:
            st.error(f"Kolom ID_Magang atau Tanggal tidak ditemukan di sheet: {e}")
            return
        
        # Cari baris yang akan dihapus
        baris_yang_dihapus = []
        for i, row in enumerate(all_values[1:], start=2):  # mulai dari baris 2
            if len(row) > max(idx_id, idx_tgl):
                row_id = str(row[idx_id]).strip()
                row_tgl = str(row[idx_tgl]).strip()
                
                # Bersihkan tanggal untuk perbandingan
                row_tgl_clean = row_tgl
                tanggal_clean = tanggal
                
                # Coba parse jika format berbeda
                if '/' in row_tgl:
                    # Format DD/MM/YYYY
                    try:
                        dt = datetime.strptime(row_tgl, '%d/%m/%Y')
                        row_tgl_clean = dt.strftime('%Y-%m-%d')
                    except:
                        pass
                
                if row_id == id_magang and (row_tgl == tanggal or row_tgl_clean == tanggal_clean):
                    baris_yang_dihapus.append(i)
        
        # Hapus baris dari yang paling bawah ke atas
        if baris_yang_dihapus:
            for baris in sorted(baris_yang_dihapus, reverse=True):
                worksheet.delete_rows(baris)
                st.write(f"🗑️ Menghapus baris {baris}")
            st.write(f"✅ Berhasil menghapus {len(baris_yang_dihapus)} baris dengan ID_Magang={id_magang}, Tanggal={tanggal}")
        else:
            st.warning(f"⚠️ Tidak menemukan baris dengan ID_Magang={id_magang}, Tanggal={tanggal}")
        
    except Exception as e:
        st.error(f"Gagal menghapus data lama: {e}")
        raise e

# =========================
# FUNGSI BANTU TANGGAL
# =========================
def parse_tanggal_ke_string(tanggal):
    """
    Mengubah input tanggal (string, datetime, pd.Timestamp) menjadi string YYYY-MM-DD.
    """
    if pd.isna(tanggal):
        return None

    if isinstance(tanggal, (datetime, pd.Timestamp)):
        return tanggal.strftime('%Y-%m-%d')

    if isinstance(tanggal, str):
        t_str = tanggal.strip()
        try:
            dt = pd.to_datetime(t_str, dayfirst=True, errors='raise')
            return dt.strftime('%Y-%m-%d')
        except:
            pass

        parts = t_str.split()
        if len(parts) == 3:
            hari, bulan_str, tahun = parts
            bulan_str = bulan_str.lower()
            if bulan_str in BULAN_INDONESIA:
                bulan = BULAN_INDONESIA[bulan_str]
                try:
                    dt = datetime(int(tahun), bulan, int(hari))
                    return dt.strftime('%Y-%m-%d')
                except:
                    pass
        return None

    try:
        return pd.to_datetime(tanggal).strftime('%Y-%m-%d')
    except:
        return None

def convert_tanggal(tanggal):
    """Mengubah berbagai format tanggal menjadi datetime."""
    if pd.isna(tanggal):
        return pd.NaT
    if isinstance(tanggal, (datetime, pd.Timestamp)):
        return tanggal
    if isinstance(tanggal, str):
        t_str = tanggal.strip()
        try:
            return pd.to_datetime(t_str, dayfirst=True, errors='raise')
        except:
            pass
        parts = t_str.split()
        if len(parts) == 3:
            hari, bulan_str, tahun = parts
            bulan_str = bulan_str.lower()
            if bulan_str in BULAN_INDONESIA:
                bulan = BULAN_INDONESIA[bulan_str]
                try:
                    return datetime(int(tahun), bulan, int(hari))
                except:
                    pass
    try:
        return pd.to_datetime(tanggal, errors='coerce')
    except:
        return pd.NaT

# =========================
# VALIDASI DATA PRESENSI
# =========================
def validasi_data(df_absen, db_magang, db_data_presensi):
    """
    Melakukan validasi data absensi sesuai alur:
      1. ID Magang harus ada di db_magang
      2. Tanggal <= tanggal akhir magang
      3. Tidak ada duplikasi (ID + Tanggal) di db_data_presensi
    """
    # Cek kolom wajib
    required_cols = ['ID_Magang', 'Tanggal']
    for col in required_cols:
        if col not in df_absen.columns:
            st.error(f"Kolom '{col}' tidak ditemukan dalam file upload.")
            return {'valid': [], 'gagal': []}

    if 'ID_Magang' not in db_magang.columns or 'Akhir' not in db_magang.columns:
        st.error("Database magang harus memiliki kolom 'ID_Magang' dan 'Akhir'.")
        return {'valid': [], 'gagal': []}

    # Buat dictionary ID -> Akhir
    db_magang_dict = {}
    for _, row in db_magang.iterrows():
        id_val = row['ID_Magang']
        try:
            id_int = int(float(id_val)) if pd.notna(id_val) else None
        except:
            id_int = None
        if id_int is not None:
            akhir_str = parse_tanggal_ke_string(row['Akhir'])
            if akhir_str is not None:
                db_magang_dict[id_int] = akhir_str

    # Buat set kombinasi (ID, Tanggal) yang sudah ada
    existing_set = set()
    for _, row in db_data_presensi.iterrows():
        id_val = row['ID_Magang']
        try:
            id_int = int(float(id_val)) if pd.notna(id_val) else None
        except:
            id_int = None
        if id_int is not None:
            tgl_str = parse_tanggal_ke_string(row['Tanggal'])
            if tgl_str is not None:
                existing_set.add((id_int, tgl_str))

    valid_rows = []
    invalid_rows = []

    for idx, row in df_absen.iterrows():
        id_magang = row['ID_Magang']
        tgl = row['Tanggal']

        tgl_str = parse_tanggal_ke_string(tgl)
        if tgl_str is None:
            row_dict = row.to_dict()
            row_dict['index'] = idx
            row_dict['alasan'] = 'Tanggal tidak valid atau kosong'
            invalid_rows.append(row_dict)
            continue

        if id_magang not in db_magang_dict:
            row_dict = row.to_dict()
            row_dict['index'] = idx
            row_dict['alasan'] = 'ID Magang tidak ditemukan di database magang'
            invalid_rows.append(row_dict)
            continue

        if tgl_str > db_magang_dict[id_magang]:
            row_dict = row.to_dict()
            row_dict['index'] = idx
            row_dict['alasan'] = f'Tanggal melebihi akhir magang ({db_magang_dict[id_magang]})'
            invalid_rows.append(row_dict)
            continue

        if (id_magang, tgl_str) in existing_set:
            row_dict = row.to_dict()
            row_dict['index'] = idx
            row_dict['alasan'] = 'Data sudah ada di database presensi'
            invalid_rows.append(row_dict)
            continue

        row_dict = row.to_dict()
        row_dict['index'] = idx
        valid_rows.append(row_dict)
        existing_set.add((id_magang, tgl_str))

    return {'valid': valid_rows, 'gagal': invalid_rows}

def simpan_data_valid(data_valid, db_data_presensi):
    """Fungsi untuk menyimpan data valid ke database"""
    col_order = list(db_data_presensi.columns)
    data_baru = []
    
    for item in data_valid:
        baris = []
        for col in col_order:
            val = item.get(col, '')
            
            if isinstance(val, float) and pd.isna(val):
                val = ''
            elif isinstance(val, (datetime, pd.Timestamp)):
                val = val.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(val, time):
                val = val.strftime('%H:%M:%S')
            
            if col == 'ID_Magang' and not isinstance(val, str):
                val = str(val) if val != '' else ''
            
            baris.append(val)
        data_baru.append(baris)
    
    try:
        append_to_sheet("data_presensi", data_baru)
        st.success(f"✅ Berhasil menyimpan {len(data_baru)} data valid ke database.")
        return True
    except Exception as e:
        st.error(f"❌ Gagal menyimpan ke database: {e}")
        return False

def update_data_duplikat(data_duplikat, df_absen, db_data_presensi):
    """
    Fungsi untuk meng-update data duplikat secara BATCH (sekaligus)
    """
    try:
        # Ambil indeks dari data yang akan diupdate
        indeks_update = []
        for item in data_duplikat:
            if 'index' in item:
                indeks_update.append(item['index'])
        
        if not indeks_update:
            st.error("Tidak dapat menemukan indeks data yang akan di-update")
            return False
            
        # Ambil data dari file upload berdasarkan indeks
        data_update = df_absen.iloc[indeks_update].to_dict('records')
        
        st.info(f"📝 Memproses {len(data_update)} data untuk diupdate secara BATCH...")
        
        # ========================================
        # 1. KUMPULKAN SEMUA ID + TANGGAL YANG AKAN DIHAPUS
        # ========================================
        hapus_list = []  # List of tuples (id_magang, tanggal_str)
        
        for item in data_duplikat:
            id_magang = str(item['ID_Magang'])
            tanggal = item['Tanggal']
            
            # Konversi tanggal ke format string
            if isinstance(tanggal, (datetime, pd.Timestamp)):
                tanggal_str = tanggal.strftime('%Y-%m-%d')
            elif hasattr(tanggal, 'strftime'):
                tanggal_str = tanggal.strftime('%Y-%m-%d')
            else:
                # Parse tanggal dari berbagai format
                tgl_parsed = parse_tanggal_ke_string(tanggal)
                tanggal_str = tgl_parsed if tgl_parsed else str(tanggal)
            
            hapus_list.append((id_magang, tanggal_str))
        
        # ========================================
        # 2. HAPUS SEMUA DATA LAMA SEKALIGUS (BATCH DELETE)
        # ========================================
        try:
            success_hapus, msg_hapus = hapus_banyak_data_dari_sheets(
                "data_presensi", 
                hapus_list
            )
            
            if not success_hapus:
                st.error(f"❌ Gagal menghapus data lama: {msg_hapus}")
                return False
            else:
                st.success(f"✅ Berhasil menghapus {len(hapus_list)} data lama")
                
        except Exception as e:
            st.error(f"❌ Error saat menghapus data lama: {str(e)}")
            return False
        
        # ========================================
        # 3. SIAPKAN DATA BARU (SAMA SEPERTI SEBELUMNYA)
        # ========================================
        col_order = list(db_data_presensi.columns)
        data_baru = []
        
        for row_dict in data_update:
            baris = []
            for col in col_order:
                val = row_dict.get(col, '')
                
                # Tangani berbagai tipe data
                if isinstance(val, float) and pd.isna(val):
                    val = ''
                elif isinstance(val, (datetime, pd.Timestamp)):
                    val = val.strftime('%Y-%m-%d')
                elif isinstance(val, time):
                    val = val.strftime('%H:%M:%S')
                
                # Pastikan ID_Magang sebagai string
                if col == 'ID_Magang' and not isinstance(val, str):
                    val = str(val) if val != '' else ''
                
                # Untuk kolom Status Terbayar, biarkan kosong
                if col == 'Status Terbayar':
                    val = ''
                
                baris.append(val)
            data_baru.append(baris)
        
        # ========================================
        # 4. SIMPAN SEMUA DATA BARU SEKALIGUS
        # ========================================
        if data_baru:
            success = append_to_sheet("data_presensi", data_baru)
            if success:
                st.success(f"✅ Berhasil menyimpan {len(data_baru)} data baru.")
                return True
            else:
                st.error("❌ Gagal menyimpan data baru ke database.")
                return False
        else:
            st.warning("Tidak ada data yang disimpan.")
            return False
        
    except Exception as e:
        st.error(f"❌ Gagal meng-update data: {str(e)}")
        return False


def hapus_banyak_data_dari_sheets(sheet_name, hapus_list):
    """
    Menghapus banyak data sekaligus dari Google Sheets berdasarkan ID_Magang dan Tanggal
    
    Args:
        sheet_name (str): Nama sheet
        hapus_list (list): List of tuples [(id_magang1, tgl1), (id_magang2, tgl2), ...]
    
    Returns:
        tuple: (success, message)
    """
    try:
        worksheet = get_worksheet(sheet_name)
        if not worksheet:
            return False, "Gagal mendapatkan worksheet"
        
        # Ambil semua data
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) <= 1:
            return False, "Sheet kosong atau hanya berisi header"
        
        header = all_values[0]
        
        # Cari indeks kolom
        try:
            idx_id = header.index('ID_Magang')
            idx_tgl = header.index('Tanggal')
        except ValueError as e:
            return False, f"Kolom ID_Magang atau Tanggal tidak ditemukan: {e}"
        
        # Buat set untuk lookup cepat
        lookup_set = set()
        for id_m, tgl in hapus_list:
            # Normalisasi tanggal
            tgl_normalized = tgl
            # Coba berbagai format
            try:
                # Coba parse ke datetime lalu format ke YYYY-MM-DD
                dt = pd.to_datetime(tgl)
                tgl_normalized = dt.strftime('%Y-%m-%d')
            except:
                pass
            
            lookup_set.add((str(id_m).strip(), tgl_normalized))
        
        # Kumpulkan baris yang akan dihapus
        baris_dihapus = []
        
        for i, row in enumerate(all_values[1:], start=2):  # mulai baris 2
            if len(row) <= max(idx_id, idx_tgl):
                continue
                
            row_id = str(row[idx_id]).strip()
            row_tgl = str(row[idx_tgl]).strip()
            
            # Normalisasi tanggal dari sheet
            row_tgl_normalized = row_tgl
            try:
                dt = pd.to_datetime(row_tgl, dayfirst=True)
                row_tgl_normalized = dt.strftime('%Y-%m-%d')
            except:
                pass
            
            # Cek apakah ada di lookup_set
            if (row_id, row_tgl_normalized) in lookup_set:
                baris_dihapus.append(i)
        
        if not baris_dihapus:
            return False, "Tidak ada data yang cocok untuk dihapus"
        
        # Hapus semua baris sekaligus (dari bawah ke atas)
        for baris in sorted(baris_dihapus, reverse=True):
            worksheet.delete_rows(baris)
        
        return True, f"Berhasil menghapus {len(baris_dihapus)} baris"
        
    except Exception as e:
        return False, str(e)
    
def hapus_data_by_periode(sheet_name, tgl_awal, tgl_akhir):
    """
    Menghapus data presensi berdasarkan periode tanggal menggunakan BATCH UPDATE
    """
    try:
        worksheet = get_worksheet(sheet_name)
        if not worksheet:
            return False, "Gagal mendapatkan worksheet", 0
        
        # Ambil semua data
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) <= 1:
            return False, "Sheet kosong atau hanya berisi header", 0
        
        header = all_values[0]
        data_rows = all_values[1:]  # Data tanpa header
        
        # Cari indeks kolom Tanggal
        try:
            tgl_col_idx = header.index('Tanggal')
        except ValueError:
            return False, "Kolom Tanggal tidak ditemukan", 0
        
        # Konversi tanggal awal/akhir
        tgl_awal_dt = pd.Timestamp(tgl_awal)
        tgl_akhir_dt = pd.Timestamp(tgl_akhir)
        
        # Siapkan data baru (HANYA data yang TIDAK dihapus)
        new_data = [header]  # Mulai dengan header
        
        for row in data_rows:
            if len(row) <= tgl_col_idx:
                new_data.append(row)
                continue
                
            tgl_str = row[tgl_col_idx].strip()
            
            try:
                tgl_dt = pd.to_datetime(tgl_str, format='%d/%m/%Y', errors='coerce')
                
                # Jika TIDAK dalam periode hapus, simpan
                if pd.isna(tgl_dt) or not (tgl_awal_dt <= tgl_dt <= tgl_akhir_dt):
                    new_data.append(row)
            except:
                new_data.append(row)
        
        jumlah_hapus = len(data_rows) - (len(new_data) - 1)  # -1 karena header
        
        if jumlah_hapus == 0:
            return False, f"Tidak ada data pada periode {tgl_awal.strftime('%d/%m/%Y')} - {tgl_akhir.strftime('%d/%m/%Y')}", 0
        
        # ============================================
        # BATCH UPDATE: KOSONGKAN SHEET DAN TULIS ULANG
        # ============================================
        # Clear seluruh sheet
        worksheet.clear()
        
        # Tulis ulang semua data (header + data yang tidak dihapus)
        worksheet.update('A1', new_data, value_input_option='USER_ENTERED')
        
        return True, f"Berhasil menghapus {jumlah_hapus} data", jumlah_hapus
        
    except Exception as e:
        return False, str(e), 0

# =========================
# FUNGSI REKAPITULASI KEHADIRAN
# =========================
def parse_time(time_str):
    """
    Mengubah string waktu 'HH:MM' menjadi objek timedelta.
    """
    if pd.isna(time_str) or time_str == '':
        return None
    try:
        t = datetime.strptime(str(time_str).strip(), '%H:%M').time()
        return timedelta(hours=t.hour, minutes=t.minute)
    except:
        return None

def hitung_umut(row, break_start=None, break_end=None):
    """
    Menghitung UMUT harian dengan mempertimbangkan jam istirahat yang dapat disesuaikan.
    """
    jam_masuk = parse_time(row['Jam Masuk'])
    jam_pulang = parse_time(row['Jam Pulang'])
    scan_masuk = parse_time(row['Scan Masuk'])
    scan_keluar = parse_time(row['Scan Keluar'])
    terlambat = row.get('Terlambat', '')

    umut = 0
    keterangan = []

    if jam_masuk is None or jam_pulang is None:
        return 0, "data jam kerja tidak lengkap"

    if scan_masuk is None and scan_keluar is None:
        return 0, "tidak masuk"
    if scan_masuk is None:
        scan_masuk = jam_masuk
        keterangan.append("scan masuk kosong")
    if scan_keluar is None:
        scan_keluar = jam_pulang
        keterangan.append("scan keluar kosong")

    def kurangi_istirahat(masuk, keluar):
        if break_start is None or break_end is None:
            return keluar - masuk
        if keluar <= break_start or masuk >= break_end:
            return keluar - masuk
        irisan_mulai = max(masuk, break_start)
        irisan_selesai = min(keluar, break_end)
        durasi_irisan = irisan_selesai - irisan_mulai
        return (keluar - masuk) - durasi_irisan

    durasi = kurangi_istirahat(scan_masuk, scan_keluar)
    durasi_jam = durasi.total_seconds() / 3600.0

    batas_toleransi = jam_masuk + timedelta(minutes=5)
    if scan_masuk > batas_toleransi:
        if str(terlambat).strip() == '1':
            keterangan.append("terlambat (tanpa keterangan)")
        else:
            keterangan.append("izin terlambat")

    if durasi_jam < 4:
        umut = 8000
        keterangan.append("durasi <4 jam")
    else:
        if scan_masuk > batas_toleransi:
            if str(terlambat).strip() == '1':
                umut = 8000
            else:
                umut = 20000
        else:
            umut = 20000

        if durasi_jam >= 12:
            if not (scan_masuk > batas_toleransi) or str(terlambat).strip() != '1':
                umut += 12000
                keterangan.append("lembur")

    ket_string = " dan ".join(keterangan) if keterangan else ""
    return umut, ket_string

def create_excel_sheet(writer, df, sheet_name, title):
    """
    Menulis DataFrame ke sheet Excel dengan judul di baris pertama.
    """
    df.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    format_title = workbook.add_format({'bold': True, 'font_size': 14})
    worksheet.write(0, 0, title, format_title)
    
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, max_len)