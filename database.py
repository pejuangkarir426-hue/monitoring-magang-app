# import streamlit as st
# import pandas as pd
# import gspread
# from google.oauth2.service_account import Credentials
# from datetime import datetime
# import hashlib
# from config import (SHEET_DITOLAK,SPREADSHEET_URL, SHEET_AKUN, SHEET_PENDAFTARAN, SHEET_DITERIMA, STATUS_MENUNGGU, STATUS_APPROVED, STATUS_DITOLAK)

# @st.cache_resource
# def init_gsheet():
#     try:
#         google_credentials = st.secrets["GOOGLE_CREDENTIALS"]
        
#         if hasattr(google_credentials, 'to_dict'):
#             creds_info = google_credentials.to_dict()
#         elif isinstance(google_credentials, dict):
#             creds_info = google_credentials
#         else:
#             import json
#             creds_info = json.loads(google_credentials)
        
#         if 'private_key' in creds_info:
#             if '\\n' in creds_info['private_key']:
#                 creds_info['private_key'] = creds_info['private_key'].replace('\\n', '\n')
        
#         creds = Credentials.from_service_account_info(
#             creds_info,
#             scopes=['https://www.googleapis.com/auth/spreadsheets']
#         )
#         client = gspread.authorize(creds)
#         sheet = client.open_by_url(SPREADSHEET_URL)
#         return sheet
#     except Exception as e:
#         st.error(f"Error koneksi Google Sheets: {e}")
#         return None

# # ---------- FUNGSI AUTHENTIKASI ----------
# def hash_password(password):
#     """Hash password sederhana"""
#     return hashlib.sha256(password.encode()).hexdigest()

# def authenticate(username, password, df_akun):
#     """Verifikasi username dan password"""
#     hashed_pass = hash_password(password)
    
#     # Cek di dataframe akun
#     user_data = df_akun[df_akun['username'].str.lower() == username.lower()]
    
#     if not user_data.empty:
#         stored_pass = user_data.iloc[0]['password']
#         # Bandingkan dengan hash
#         return stored_pass == hashed_pass or stored_pass == password  # Support plain text juga
#     return False

# # ---------- FUNGSI CRUD GOOGLE SHEETS ----------
# def load_data(sheet_instance, sheet_name):
#     """Load data dari Google Sheets"""
#     try:
#         worksheet = sheet_instance.worksheet(sheet_name)
#         data = worksheet.get_all_records()
#         return pd.DataFrame(data) if data else pd.DataFrame()
#     except gspread.exceptions.WorksheetNotFound:
#         # Buat worksheet jika belum ada
#         if sheet_name == SHEET_DITERIMA:
#             sheet_instance.add_worksheet(title=sheet_name, rows=100, cols=20)
#             return pd.DataFrame()
#         else:
#             st.error(f"Sheet '{sheet_name}' tidak ditemukan!")
#             return None

# # ---------- FUNGSI UPDATE STATUS (DENGAN REJECT) ----------
# def update_status(sheet_instance, sheet_name, row_index, status, df_data):
#     """Update status di sheet pendaftaran"""
#     try:
#         worksheet = sheet_instance.worksheet(sheet_name)
        
#         # Ambil semua data untuk mencari baris yang tepat
#         all_data = worksheet.get_all_values()
        
#         # Validasi row_index
#         if row_index >= len(df_data):
#             st.error(f"Index {row_index} melebihi jumlah data {len(df_data)}")
#             return False
            
#         id_target = str(df_data.iloc[row_index]['ID_Pendaftar'])
#         nama_target = df_data.iloc[row_index]['Nama']
#         waktu_target = str(df_data.iloc[row_index]['Waktu Daftar'])  # Konversi ke string
        
#         # DEBUG: Tampilkan info pencarian
#         print(f"Mencari - ID: {id_target}, Nama: {nama_target}, Waktu: {waktu_target}")
        
#         target_row = None
#         for i, row in enumerate(all_data):
#             if i == 0:  # skip header
#                 continue
#             if len(row) > 3:  # Minimal punya 3 kolom
#                 # Bersihkan data untuk perbandingan
#                 row_id = str(row[0]).strip() if len(row) > 0 else ""
#                 row_waktu = str(row[1]).strip() if len(row) > 1 else ""
#                 row_nama = str(row[2]).strip() if len(row) > 2 else ""
                
#                 if (row_id == id_target and 
#                     row_waktu == waktu_target and 
#                     row_nama == nama_target):
#                     target_row = i + 1
#                     print(f"Ditemukan di baris: {target_row}")
#                     break
        
#         if target_row is None:
#             # Coba cari berdasarkan ID saja
#             for i, row in enumerate(all_data):
#                 if i == 0:
#                     continue
#                 if len(row) > 0 and str(row[0]).strip() == id_target:
#                     target_row = i + 1
#                     print(f"Ditemukan berdasarkan ID di baris: {target_row}")
#                     break
            
#             if target_row is None:
#                 st.error(f"Tidak dapat menemukan baris untuk {nama_target} (ID: {id_target})")
#                 return False
        
#         # CARI TAHU INDEX KOLOM STATUS
#         headers = all_data[0]
#         status_col_index = None
#         for idx, header in enumerate(headers):
#             if header.strip().lower() == 'status':
#                 status_col_index = idx + 1  # Google Sheets uses 1-based index
#                 break
        
#         if status_col_index is None:
#             # Jika tidak ditemukan, asumsikan kolom ke-13
#             status_col_index = 13
#             print("Kolom Status tidak ditemukan, menggunakan asumsi kolom 13")
        
#         # UPDATE STATUS
#         worksheet.update_cell(target_row, status_col_index, status)
#         print(f"Status diupdate di baris {target_row}, kolom {status_col_index} menjadi {status}")
        
#         # HANDLE BERDASARKAN STATUS
#         if status == STATUS_APPROVED:
#             # Salin ke sheet diterima
#             try:
#                 worksheet_diterima = sheet_instance.worksheet(SHEET_DITERIMA)
#             except gspread.exceptions.WorksheetNotFound:
#                 worksheet_diterima = sheet_instance.add_worksheet(title=SHEET_DITERIMA, rows=1000, cols=30)
#                 headers_sheet = df_data.columns.tolist() + ['Tanggal_Approved']
#                 worksheet_diterima.append_row(headers_sheet)
            
#             # Ambil data baris
#             row_data_raw = worksheet.row_values(target_row)
            
#             # Buat dictionary dengan semua header
#             row_dict = {}
#             for j, header in enumerate(headers):
#                 if j < len(row_data_raw):
#                     row_dict[header] = row_data_raw[j]
#                 else:
#                     row_dict[header] = ""
            
#             # Tambah tanggal approved
#             row_dict['Tanggal_Approved'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
#             # Cek apakah data sudah ada di sheet diterima
#             data_diterima = worksheet_diterima.get_all_values()
#             id_exists = False
#             for i, r in enumerate(data_diterima):
#                 if i == 0:
#                     continue
#                 if len(r) > 0 and str(r[0]) == id_target:
#                     id_exists = True
#                     # Update data yang ada
#                     for col_idx, (key, value) in enumerate(row_dict.items()):
#                         if col_idx < len(r):
#                             worksheet_diterima.update_cell(i + 1, col_idx + 1, value)
#                     break
            
#             if not id_exists:
#                 worksheet_diterima.append_row(list(row_dict.values()))
            
#             # Hapus dari sheet ditolak
#             hapus_dari_sheet_ditolak(sheet_instance, id_target)
            
#         elif status == STATUS_DITOLAK:
#             # SIMPAN KE SHEET DITOLAK
#             try:
#                 worksheet_ditolak = sheet_instance.worksheet(SHEET_DITOLAK)
#             except gspread.exceptions.WorksheetNotFound:
#                 worksheet_ditolak = sheet_instance.add_worksheet(title=SHEET_DITOLAK, rows=1000, cols=30)
#                 headers_sheet = df_data.columns.tolist() + ['Tanggal_Ditolak']
#                 worksheet_ditolak.append_row(headers_sheet)
            
#             # Ambil data baris
#             row_data_raw = worksheet.row_values(target_row)
            
#             # Buat dictionary dengan semua header
#             row_dict = {}
#             for j, header in enumerate(headers):
#                 if j < len(row_data_raw):
#                     row_dict[header] = row_data_raw[j]
#                 else:
#                     row_dict[header] = ""
            
#             # Tambah informasi penolakan
#             row_dict['Tanggal_Ditolak'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
#             # Cek apakah data sudah ada di sheet ditolak
#             data_ditolak = worksheet_ditolak.get_all_values()
#             id_exists = False
#             for i, r in enumerate(data_ditolak):
#                 if i == 0:
#                     continue
#                 if len(r) > 0 and str(r[0]) == id_target:
#                     id_exists = True
#                     # Update data yang ada
#                     for col_idx, (key, value) in enumerate(row_dict.items()):
#                         if col_idx < len(r):
#                             worksheet_ditolak.update_cell(i + 1, col_idx + 1, value)
#                     break
            
#             if not id_exists:
#                 worksheet_ditolak.append_row(list(row_dict.values()))
            
#             # Hapus dari sheet diterima
#             hapus_dari_sheet_diterima(sheet_instance, id_target)
            
#         elif status == STATUS_MENUNGGU:  # Untuk tombol RESET
#             # Hapus dari kedua sheet
#             hapus_dari_sheet_diterima(sheet_instance, id_target)
#             hapus_dari_sheet_ditolak(sheet_instance, id_target)
            
#         return True
        
#     except Exception as e:
#         st.error(f"Error update status: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return False

# def hapus_dari_sheet_ditolak(sheet_instance, id_pendaftar):
#     """Hapus data dari sheet ditolak berdasarkan ID_Pendaftar"""
#     try:
#         worksheet_ditolak = sheet_instance.worksheet(SHEET_DITOLAK)
#         data_ditolak = worksheet_ditolak.get_all_values()
        
#         for i, row in enumerate(data_ditolak):
#             if i == 0:  # skip header
#                 continue
#             if len(row) > 0 and str(row[0]).strip() == str(id_pendaftar).strip():
#                 worksheet_ditolak.delete_rows(i + 1)
#                 print(f"Data {id_pendaftar} dihapus dari sheet ditolak")
#                 return True
#     except gspread.exceptions.WorksheetNotFound:
#         pass
#     except Exception as e:
#         print(f"Error hapus dari ditolak: {e}")
#     return False

# def hapus_dari_sheet_diterima(sheet_instance, id_pendaftar):
#     """Hapus data dari sheet diterima berdasarkan ID_Pendaftar"""
#     try:
#         worksheet_diterima = sheet_instance.worksheet(SHEET_DITERIMA)
#         data_diterima = worksheet_diterima.get_all_values()
        
#         for i, row in enumerate(data_diterima):
#             if i == 0:  # skip header
#                 continue
#             if len(row) > 0 and str(row[0]).strip() == str(id_pendaftar).strip():
#                 worksheet_diterima.delete_rows(i + 1)
#                 print(f"Data {id_pendaftar} dihapus dari sheet diterima")
#                 return True
#     except gspread.exceptions.WorksheetNotFound:
#         pass
#     except Exception as e:
#         print(f"Error hapus dari diterima: {e}")
#     return False