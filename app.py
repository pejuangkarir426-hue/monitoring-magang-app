import streamlit as st
import pandas as pd
from datetime import datetime, time  # time adalah tipe datetime.time
import time as mod_time  # alias untuk modul time
from dateutil.relativedelta import relativedelta
from utils import (
    authenticate_user1, save_internship_data, create_excel_sheet, load_data_cached, get_worksheet,load_data_for_login, update_data_duplikat, delete_internship_data,
    load_data, convert_tanggal, append_to_sheet, validasi_data, hitung_umut, update_internship_data, parse_tanggal_ke_string, refresh_data_in_session, parse_time, hapus_data_by_periode
)
from config import SPREADSHEET_ID, DEPARTEMEN, APP_CONFIG, MESSAGES, departemen_list, jenissekolah_list, periode_list, nama_kolom_data_absen
import plotly.express as px
import plotly.graph_objects as go
import re
import time as tm
from io import BytesIO
from google.oauth2.service_account import Credentials
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title=APP_CONFIG['nama_aplikasi'],
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS STYLE (SESUAI DENGAN YANG DIBERIKAN)
# =========================
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animasi cahaya bergerak */
    @keyframes shineEffect {
        0% { left: -100%; }
        100% { left: 120%; }
    }
    
    /* Premium Header */
    .premium-header {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #FC5000 0%, #FC5000 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    .premium-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 60%;
        height: 100%;
        background: linear-gradient(
            120deg,
            rgba(255,255,255,0) 0%,
            rgba(255,255,255,0.4) 50%,
            rgba(255,255,255,0) 100%
        );
        transform: skewX(-25deg);
        animation: shineEffect 3.5s infinite;
    }
    
    .premium-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    /* Progress Tracker Premium */
    .progress-premium {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin: 2rem 0;
    }
    
    .step-indicator {
        display: flex;
        justify-content: space-between;
        position: relative;
        margin: 2rem 0;
    }
    
    .step-indicator::before {
        content: '';
        position: absolute;
        top: 30px;
        left: 0;
        width: 100%;
        height: 4px;
        background: #e0e0e0;
        z-index: 1;
    }
    
    .step-item {
        flex: 1;
        text-align: center;
        position: relative;
        z-index: 2;
    }
    
    .step-badge {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: white;
        border: 4px solid #e0e0e0;
        margin: 0 auto 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: 700;
        color: #666;
        transition: all 0.3s ease;
        position: relative;
        background: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .step-badge.completed {
        background: #4caf50;
        border-color: #4caf50;
        color: white;
        animation: pulse 1s;
    }
    
    .step-badge.active {
        border-color: #FC5000;
        color: #FC5000;
        transform: scale(1.1);
        box-shadow: 0 0 0 6px rgba(252, 80, 0, 0.2);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    /* Form Premium */
    .premium-form {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    
    .form-section {
        background: #f8faff;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid rgba(252, 80, 0, 0.1);
    }
    
    .form-section h3 {
        color: #333;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .form-section h3 i {
        color: #FC5000;
    }
    
    /* Cards */
    .premium-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.03);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    
    .info-card {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6d5 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FC5000;
    }
    
    .success-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4caf50;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ff9800;
    }
    
    /* Login Styles */
    .login-container {
        max-width: 450px;
        margin: 5rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: slideUp 0.5s ease;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        color: #FC5000;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .login-header i {
        font-size: 3rem;
        color: #FC5000;
        margin-bottom: 1rem;
    }
    
    /* Sidebar Styles */
    .sidebar-profile {
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .sidebar-profile i {
        font-size: 3rem;
        color: #FC5000;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-profile h4 {
        color: #333;
        margin-bottom: 0.25rem;
    }
    
    .sidebar-profile p {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0;
    }
    
    /* Dashboard Styles */
    .dashboard-header {
        background: linear-gradient(135deg, #FC5000 0%, #FF7A00 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(252, 80, 0, 0.3);
    }
    
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: 1px solid #f0f0f0;
        transition: transform 0.3s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    </style>
    
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)

# =========================
# INISIALISASI SESSION STATE
# =========================
def init_session_state():
    defaults = {
        'logged_in': False,
        'username': None,
        'user_data': None,
        'current_page': 'login',
        'progress_step': 1,
        'form_submitted': False,
        'documents_verified': False,
        'form_data': {},
        'registration_number': None,
        'selected_dept': ''
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# =========================
# SIDEBAR

def show_sidebar():
    st.markdown("""
    <style>

    /* Hapus padding default sidebar */
    [data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }

    /* Background sidebar */
    [data-testid="stSidebar"] {
        background-color: white;
    }

    /* Semua teks putih */
    [data-testid="stSidebar"] * {
        color: black !important;
    }

    /* Hilangkan circle radio */
    div[role="radiogroup"] label > div:first-child {
        display: none;
    }

    /* Hapus padding radio group */
    div[role="radiogroup"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Style menu item */
    div[role="radiogroup"] label {
        width: 100% !important;
        display: block;
        padding: 16px 20px;
        margin: 0;
        border-radius: 0;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        color: black !important;
    }

    /* Hover */
    div[role="radiogroup"] label:hover {
        background-color: #1C2B0;
    }

    /* Active */
    div[role="radiogroup"] label:has(input:checked) {
        background-color: #FC5000;
        color: white !important;
    }

    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Logo
        st.image("assets/Logo japfa tanpa BG.png", width=100)

        st.markdown(
        """
        <hr style="
            border:1.5px solid #2D7DAF;
            margin:6px 0;
        ">
        """,
        unsafe_allow_html=True
        )

        # Menu
        menu = st.radio(
            " ",
            [
                "Entry Data",
                "Magang Analytic",
                "Update Presensi",
                "Rekapitulasi Kehadiran",
                "Monitoring Timebreak"
            ]
        )

        # Mapping halaman
        menu_map = {
            "Entry Data": "pendaftaran",
            "Magang Analytic": "Magang Analytic",
            "Update Presensi": "Update Presensi",
            "Rekapitulasi Kehadiran": "Rekapitulasi Kehadiran",
            "Monitoring Timebreak": "monitoring_timebreak"
        }

        selected_page = menu_map[menu]

        # Reset form jika Entry Data
        if selected_page == "pendaftaran":
            st.session_state.progress_step = 1
            st.session_state.form_submitted = False
            st.session_state.documents_verified = False
            st.session_state.form_data = {}
            st.session_state.registration_number = None

        st.session_state.current_page = selected_page

        st.markdown("---")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄", use_container_width=True):
                with st.spinner("Memperbarui cache..."):
                    # Clear cache
                    st.cache_data.clear()
                    # Reload data ke session state
                    st.session_state.data_magang = load_data_cached("database_magang")
                    st.session_state.data_presensi = load_data_cached("data_presensi")
                    st.session_state.data_departemen = load_data_cached("departemen")
                    st.session_state.data_subdepartemen = load_data_cached("sub_departemen")
                st.success("✅ Data berhasil diperbarui!")
                tm.sleep(1)
                st.rerun()
            
        with col2:
            # Tombol Logout
            if st.button("Keluar", use_container_width=True):
                logout()
        
        # Tampilkan info kapan terakhir di-refresh (opsional)
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")
        st.caption(f"Terakhir update: {st.session_state.last_refresh}")


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# =========================
# HALAMAN LOGIN
# =========================
def halaman_login():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <i class="fas fa-user-graduate"></i>
                <h1>JAPFA Internship</h1>
                <p>Program Magang PT Japfa Comfeed Indonesia Tbk</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="Masukkan username Anda",
                help="Gunakan username yang sudah terdaftar"
            ).strip()
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Masukkan password Anda"
            ).strip()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("MASUK", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("❌ Username dan password harus diisi!")
                else:
                    with st.spinner("🔍 Memverifikasi..."):
                        auth_result = authenticate_user1(username, password)
                        
                        if auth_result["success"]:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.user_data = auth_result.get('user_data', {})
                            
                            with st.spinner("📊 Memuat data aplikasi..."):
                                try:
                                    # Gunakan fungsi yang di-cache
                                    st.session_state.data_magang = load_data_cached("database_magang")
                                    st.session_state.data_presensi = load_data_cached("data_presensi")
                                    st.session_state.data_departemen = load_data_cached("departemen")
                                    st.session_state.data_subdepartemen = load_data_cached("sub_departemen")
                                except Exception as e:
                                    st.error(f"Gagal memuat data: {e}")
                                    return

                            st.session_state.current_page = 'status_kuota'
                            st.success("✅ Login berhasil!")
                            tm.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(f"❌ {auth_result['message']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HALAMAN PENDAFTARAN
# =========================
def halaman_entry_data():
    st.markdown("""
    <div class="premium-header">
        <h1><i class="fas fa-user-graduate"></i> Program Magang JAPFA</h1>
        <p>PT Japfa Comfeed Indonesia Tbk - Sidoarjo</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Tab utama
    st.markdown("""
    <style>

    /* Jarak antar tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    /* Tab default (BELUM DIKLIK) */
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border: 2px solid #D1D5DB;   /* <-- border abu */
        border-radius: 12px;
        padding: 10px 22px;
        font-weight: 600;
        color: #374151;
        transition: all 0.3s ease;
    }

    /* Hover */
    .stTabs [data-baseweb="tab"]:hover {
        border: 2px solid #FC5000;
        color: #FC5000;
    }

    /* Tab aktif (yang diklik) */
    .stTabs [aria-selected="true"] {
        background-color: #FC5000 !important;
        color: white !important;
        border: 2px solid #FC5000 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }

    </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Input Data", "Edit Data"])
    with tab1:
        df_dept = st.session_state.data_departemen
        df_subdept = st.session_state.data_subdepartemen
        departemen_list = df_dept["nama_departemen"].tolist()
        # load_data(sheet_name)
        
        # =============================
        # DATA PRIBADI
        # =============================
        with st.container():
            st.subheader("Data Pribadi")
            
            col1, col2 = st.columns(2)
            
            with col1:
                id_magang = st.text_input("ID Magang *", placeholder="Contoh: MGT-001")
                nama = st.text_input("Nama *", placeholder="Sesuai KTP")
                jenis_kelamin = st.selectbox("Jenis Kelamin *", ["Laki-laki", "Perempuan"])
                jurusan = st.text_input("Jurusan *", placeholder="Contoh: Teknik Informatika")
                jenjang = st.selectbox("Jenjang *", ["SMA/SMK", "D3", "D4", "S1", "S2"])
            
            with col2:
                sekolah = st.text_input("Sekolah/Universitas *", placeholder="Nama institusi")
                jenis_univ_sekolah = st.selectbox("Jenis Sekolah/Univ *", jenissekolah_list)
                dept = st.selectbox("Departemen *", departemen_list, key="dept")
                
                # mengambil id_departemen
                id_dept = df_dept[df_dept["nama_departemen"] == dept]["id_departemen"].values[0]
                # filter subdepartemen berdasarkan departemen
                subdept_options = df_subdept[df_subdept["id_departemen"] == id_dept]["nama_subdepartmen"].tolist()
                subdept = st.selectbox("Sub Departemen *", subdept_options)
                
                keterangan = st.text_input("Keterangan *", placeholder="Keterangan tambahan")
        
        st.divider()
        
        # =============================
        # JADWAL MAGANG
        # =============================
        with st.container():
            st.subheader("Jadwal Magang")
            
            col3, col4 = st.columns(2)
            now = datetime.now().date()
            
            with col3:
                tgl_mulai = st.date_input(
                    "Tanggal Mulai *",
                    value=now
                )
                durasi = st.selectbox("Durasi (bulan) *", [3, 4, 5, 6])
                tgl_akhir_otomatis = tgl_mulai + relativedelta(months=durasi)       
                st.info(f"Rekomendasi : **{tgl_akhir_otomatis.strftime('%d/%m/%Y')}**")
            
            with col4:
                
                tgl_akhir = st.date_input(
                    "Tanggal Akhir (opsional)",
                    value=tgl_akhir_otomatis,
                    min_value=tgl_mulai
                )

                periode = st.selectbox("Periode *", periode_list)
        
        st.divider()
        
        # =============================
        # PREVIEW & SUBMIT
        # =============================
        with st.expander("👀 Preview Data", expanded=False):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.write(f"**ID:** {id_magang or '-'}")
                st.write(f"**Nama:** {nama or '-'}")
                st.write(f"**Jenis Kelamin:** {jenis_kelamin}")
                st.write(f"**Jurusan:** {jurusan or '-'}")
                st.write(f"**Jenjang:** {jenjang}")
                st.write(f"**Sekolah:** {sekolah or '-'}")
            with col_p2:
                st.write(f"**Jenis Sekolah:** {jenis_univ_sekolah}")
                st.write(f"**Dept:** {dept}")
                st.write(f"**Subdept:** {subdept}")
                st.write(f"**Bulan:** {durasi}")
                st.write(f"**Periode:** {periode}")
                st.write(f"**Keterangan:** {keterangan or '-'}")
            
            st.write(f"**Jadwal:** {tgl_mulai.strftime('%d/%m/%Y')} - {tgl_akhir.strftime('%d/%m/%Y')} ({durasi} bulan)")
        
        # Tombol Submit
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            if st.button("DAFTAR SEKARANG", use_container_width=True, type="primary"):
                # Validasi sederhana
                if not all([id_magang, nama, jurusan, sekolah]):
                    st.error("❌ Semua field wajib harus diisi!")
                else:
                    # Siapkan data
                    bulan_indo = [
                        "Januari","Februari","Maret","April","Mei","Juni",
                        "Juli","Agustus","September","Oktober","November","Desember"
                    ]
                    tgl_mulai_format = f"{tgl_mulai.day} {bulan_indo[tgl_mulai.month-1]} {tgl_mulai.year}"
                    tgl_akhir_format = f"{tgl_akhir.day} {bulan_indo[tgl_akhir.month-1]} {tgl_akhir.year}"
                    form_data = {
                        "id_magang": id_magang,
                        "nama": nama,
                        "jenis_kelamin": jenis_kelamin,
                        "jurusan": jurusan,
                        "jenjang": jenjang,
                        "sekolah": sekolah,
                        "jenis_sekolah": jenis_univ_sekolah,
                        "bagian_dept": dept,
                        "sub_dept": subdept,
                        "bulan": durasi,
                        "tgl_mulai": tgl_mulai_format,
                        "tgl_akhir": tgl_akhir_format,
                        "periode": periode,
                        "tahun": tgl_mulai.year,
                        "keterangan": keterangan
                    }
                    
                    # Simpan
                    if save_internship_data(form_data):
                        st.success("✅ Pendaftaran berhasil!")
                        st.balloons()
                        tm.sleep(2)
                        st.rerun()

    with tab2:
        st.title("✏️ Edit & Hapus Data Magang")
        
        # Inisialisasi session state untuk edit mode dan hapus mode
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False
        if 'delete_confirmation' not in st.session_state:
            st.session_state.delete_confirmation = False
        if 'selected_data' not in st.session_state:
            st.session_state.selected_data = None
        if 'data_to_delete' not in st.session_state:
            st.session_state.data_to_delete = None
        
        # Load data yang diperlukan
        df_magang = st.session_state.data_magang
        df_dept = st.session_state.data_departemen
        df_subdept = st.session_state.data_subdepartemen
        
        if len(df_magang) > 0:
            # =============================
            # FILTER PENCARIAN
            # =============================
            with st.container():
                st.subheader("🔍 Pencarian Data")
                
                col_search1, col_search2, col_search3 = st.columns([2, 2, 1])
                
                with col_search1:
                    search_id = st.text_input("Cari ID Magang", placeholder="Masukkan ID Magang...", key="search_id_edit")
                
                with col_search2:
                    search_nama = st.text_input("Cari Nama", placeholder="Masukkan Nama...", key="search_nama_edit")
                
                with col_search3:
                    search_button = st.button("🔎 Cari", use_container_width=True, key="search_btn_edit")
                
                # Filter data berdasarkan pencarian
                filtered_df = df_magang.copy()
                
                if search_id:
                    filtered_df = filtered_df[filtered_df['ID_Magang'].astype(str).str.contains(search_id, case=False, na=False)]
                
                if search_nama:
                    filtered_df = filtered_df[filtered_df['Nama'].astype(str).str.contains(search_nama, case=False, na=False)]
                
                # Tampilkan hasil pencarian
                if search_id or search_nama:
                    st.write(f"Ditemukan **{len(filtered_df)}** data")
            
            st.divider()
            
            # =============================
            # PILIH DATA YANG AKAN DIEDIT/DHAPUS
            # =============================
            if len(filtered_df) > 0:
                # Pilih data
                selected_id = st.selectbox(
                    "📋 Pilih Data:",
                    options=filtered_df['ID_Magang'].tolist(),
                    format_func=lambda x: f"{x} - {filtered_df[filtered_df['ID_Magang']==x]['Nama'].values[0]}",
                    key="select_id_edit"
                )
                
                # Tampilkan informasi data yang dipilih
                selected_data_preview = filtered_df[filtered_df['ID_Magang'] == selected_id].iloc[0]
                
                with st.container(border=True):
                    col_preview1, col_preview2 = st.columns(2)
                    with col_preview1:
                        st.write(f"**ID Magang:** {selected_data_preview['ID_Magang']}")
                        st.write(f"**Nama:** {selected_data_preview['Nama']}")
                        st.write(f"**Departemen:** {selected_data_preview['Bagian/Dept']}")
                    with col_preview2:
                        st.write(f"**Sub Dept:** {selected_data_preview.get('Sub Dept', '-')}")
                        st.write(f"**Periode:** {selected_data_preview.get('Periode', '-')}")
                        st.write(f"**Tahun:** {selected_data_preview.get('Tahun', '-')}")
                
                # Tombol Aksi: EDIT dan HAPUS
                col_action1, col_action2, col_action3 = st.columns([1, 1, 2])
                
                with col_action1:
                    if st.button("✏️ UBAH DATA", use_container_width=True, type="primary", key="btn_edit_data"):
                        # Load data untuk diedit
                        st.session_state.selected_data = filtered_df[filtered_df['ID_Magang'] == selected_id].iloc[0].to_dict()
                        st.session_state.edit_mode = True
                        st.session_state.delete_confirmation = False
                        st.rerun()
                
                with col_action2:
                    if st.button("🗑️ HAPUS DATA", use_container_width=True, type="secondary", key="btn_delete_data"):
                        # Tampilkan konfirmasi hapus
                        st.session_state.data_to_delete = filtered_df[filtered_df['ID_Magang'] == selected_id].iloc[0].to_dict()
                        st.session_state.delete_confirmation = True
                        st.session_state.edit_mode = False
                        st.rerun()
                
                st.divider()
                
                # =============================
                # KONFIRMASI HAPUS DATA
                # =============================
                if st.session_state.delete_confirmation and st.session_state.data_to_delete:
                    data_hapus = st.session_state.data_to_delete
                    
                    with st.container(border=True):
                        st.error("⚠️ **KONFIRMASI HAPUS DATA**")
                        st.warning(f"Anda akan menghapus data berikut:")
                        
                        col_hapus1, col_hapus2 = st.columns(2)
                        with col_hapus1:
                            st.write(f"**ID Magang:** {data_hapus['ID_Magang']}")
                            st.write(f"**Nama:** {data_hapus['Nama']}")
                            st.write(f"**Departemen:** {data_hapus['Bagian/Dept']}")
                        
                        with col_hapus2:
                            st.write(f"**Sub Dept:** {data_hapus.get('Sub Dept', '-')}")
                            st.write(f"**Periode:** {data_hapus.get('Periode', '-')}")
                            st.write(f"**Tahun:** {data_hapus.get('Tahun', '-')}")
                        
                        st.error("⚠️ Tindakan ini **TIDAK DAPAT DIBATALKAN** dan akan menghapus data secara permanen dari database!")
                        
                        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                        
                        with col_btn1:
                            if st.button("❌ Batal", use_container_width=True, key="cancel_delete_btn"):
                                st.session_state.delete_confirmation = False
                                st.session_state.data_to_delete = None
                                st.rerun()
                        
                        with col_btn2:
                            if st.button("🗑️ Ya, Hapus Data", use_container_width=True, type="primary", key="confirm_delete_btn"):
                                with st.spinner("Menghapus data..."):
                                    try:
                                        # Panggil fungsi hapus data dari utils.py
                                        # Anda perlu membuat fungsi delete_internship_data di utils.py
                                        success = delete_internship_data(data_hapus['ID_Magang'])
                                        
                                        if success:
                                            st.session_state.delete_confirmation = False
                                            st.session_state.data_to_delete = None
                                            st.success(f"✅ Data {data_hapus['ID_Magang']} - {data_hapus['Nama']} berhasil dihapus!")
                                            
                                            # Refresh data
                                            refresh_data_in_session()
                                            tm.sleep(2)
                                            st.rerun()
                                        else:
                                            st.error("❌ Gagal menghapus data!")
                                    except Exception as e:
                                        st.error(f"❌ Error: {e}")
            
            else:
                if len(filtered_df) == 0 and (search_id or search_nama):
                    st.warning("⚠️ Tidak ada data yang sesuai dengan pencarian")
                
                # Tampilkan semua data sebagai referensi
                with st.expander("📊 Lihat Semua Data", expanded=False):
                    st.dataframe(df_magang, use_container_width=True)
        else:
            st.info("📭 Belum ada data magang")
        
        # =============================
        # FORM EDIT DATA (ditampilkan jika edit_mode = True)
        # =============================
        if st.session_state.edit_mode and st.session_state.selected_data:
            selected_data = st.session_state.selected_data
            
            st.subheader("✏️ Form Edit Data")
            st.info(f"Mengedit data: **{selected_data['ID_Magang']} - {selected_data['Nama']}**")
            
            # Tombol untuk membatalkan edit
            if st.button("❌ Batal Edit", key="cancel_edit_btn"):
                st.session_state.edit_mode = False
                st.session_state.selected_data = None
                st.rerun()
            
            st.divider()
            
            # =============================
            # DATA PRIBADI
            # =============================
            with st.container():
                st.markdown("##### 📋 Data Pribadi")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_id_magang = st.text_input(
                        "ID Magang *", 
                        value=selected_data['ID_Magang'],
                        disabled=True,
                        help="ID Magang tidak dapat diubah",
                        key="edit_id_magang"
                    )
                    edit_nama = st.text_input(
                        "Nama *", 
                        value=selected_data['Nama'],
                        placeholder="Sesuai KTP",
                        key="edit_nama"
                    )
                    
                    jk_index = 0 if selected_data['Jenis Kelamin'] == "Laki-laki" else 1
                    edit_jenis_kelamin = st.selectbox(
                        "Jenis Kelamin *", 
                        ["Laki-laki", "Perempuan"],
                        index=jk_index,
                        key="edit_jenis_kelamin"
                    )
                    
                    edit_jurusan = st.text_input(
                        "Jurusan *", 
                        value=selected_data['Jurusan/Fakultas'],
                        placeholder="Contoh: Teknik Informatika",
                        key="edit_jurusan"
                    )
                    
                    jenjang_options = ["SMA/SMK", "D3", "D4", "S1", "S2"]
                    try:
                        jenjang_index = jenjang_options.index(selected_data['Jenjang']) if selected_data['Jenjang'] in jenjang_options else 0
                    except:
                        jenjang_index = 0
                    edit_jenjang = st.selectbox(
                        "Jenjang *", 
                        jenjang_options,
                        index=jenjang_index,
                        key="edit_jenjang"
                    )
                
                with col2:
                    edit_sekolah = st.text_input(
                        "Sekolah/Universitas *", 
                        value=selected_data['Sekolah/Universitas'],
                        placeholder="Nama institusi",
                        key="edit_sekolah"
                    )
                    
                    jenis_sekolah_options = ["Universitas", "Sekolah"]
                    try:
                        jenis_index = jenis_sekolah_options.index(selected_data['Jenis Univ/Sekolah']) if selected_data['Jenis Univ/Sekolah'] in jenis_sekolah_options else 0
                    except:
                        jenis_index = 0
                    edit_jenis_univ_sekolah = st.selectbox(
                        "Jenis Sekolah/Univ *", 
                        jenis_sekolah_options,
                        index=jenis_index,
                        key="edit_jenis_univ"
                    )
                    
                    departemen_list = df_dept["nama_departemen"].tolist()
                    try:
                        dept_index = departemen_list.index(selected_data['Bagian/Dept']) if selected_data['Bagian/Dept'] in departemen_list else 0
                    except:
                        dept_index = 0
                    edit_dept = st.selectbox(
                        "Departemen *", 
                        departemen_list,
                        index=dept_index,
                        key="edit_dept"
                    )
                    
                    id_dept = df_dept[df_dept["nama_departemen"] == edit_dept]["id_departemen"].values[0]
                    subdept_options = df_subdept[df_subdept["id_departemen"] == id_dept]["nama_subdepartmen"].tolist()
                    
                    try:
                        if selected_data['Sub Dept'] in subdept_options:
                            subdept_index = subdept_options.index(selected_data['Sub Dept'])
                        else:
                            subdept_index = 0
                    except:
                        subdept_index = 0
                    
                    edit_subdept = st.selectbox(
                        "Sub Departemen *", 
                        subdept_options,
                        index=subdept_index,
                        key="edit_subdept"
                    )
                    
                    edit_keterangan = st.text_input(
                        "Keterangan", 
                        value=selected_data.get('Keterangan', ''),
                        placeholder="Keterangan tambahan (opsional)",
                        key="edit_keterangan"
                    )
            
            st.divider()
            
            # =============================
            # JADWAL MAGANG
            # =============================
            with st.container():
                st.markdown("##### 📅 Jadwal Magang")
                
                bulan_indo = {
                    'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 'Mei': 5, 'Juni': 6,
                    'Juli': 7, 'Agustus': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
                }
                
                # Parse tanggal mulai
                try:
                    tgl_mulai_parts = str(selected_data['Mulai']).split()
                    if len(tgl_mulai_parts) == 3:
                        day = int(tgl_mulai_parts[0])
                        month = bulan_indo[tgl_mulai_parts[1]]
                        year = int(tgl_mulai_parts[2])
                        tgl_mulai_default = datetime(year, month, day).date()
                    else:
                        tgl_mulai_default = datetime.now().date()
                except:
                    tgl_mulai_default = datetime.now().date()
                
                # Parse tanggal akhir
                try:
                    tgl_akhir_parts = str(selected_data['Akhir']).split()
                    if len(tgl_akhir_parts) == 3:
                        day = int(tgl_akhir_parts[0])
                        month = bulan_indo[tgl_akhir_parts[1]]
                        year = int(tgl_akhir_parts[2])
                        tgl_akhir_default = datetime(year, month, day).date()
                    else:
                        tgl_akhir_default = datetime.now().date()
                except:
                    tgl_akhir_default = datetime.now().date()
                
                col3, col4 = st.columns(2)
                
                with col3:
                    edit_tgl_mulai = st.date_input(
                        "Tanggal Mulai *",
                        value=tgl_mulai_default,
                        key="edit_tgl_mulai"
                    )
                    
                    durasi_options = [3, 4, 5, 6]
                    try:
                        current_durasi = int(selected_data['Bulan'])
                        durasi_index = durasi_options.index(current_durasi) if current_durasi in durasi_options else 0
                    except:
                        durasi_index = 0
                        
                    edit_durasi = st.selectbox(
                        "Durasi (bulan) *", 
                        durasi_options,
                        index=durasi_index,
                        key="edit_durasi"
                    )
                    
                    tgl_akhir_otomatis = edit_tgl_mulai + relativedelta(months=edit_durasi)
                    st.info(f"Rekomendasi : **{tgl_akhir_otomatis.strftime('%d/%m/%Y')}**")
                
                with col4:
                    edit_tgl_akhir = st.date_input(
                        "Tanggal Akhir",
                        value=tgl_akhir_default,
                        min_value=edit_tgl_mulai,
                        key="edit_tgl_akhir"
                    )
                    
                    periode_options = ["Semester I", "Semester II"]
                    try:
                        periode_index = periode_options.index(selected_data['Periode']) if selected_data['Periode'] in periode_options else 0
                    except:
                        periode_index = 0
                    edit_periode = st.selectbox(
                        "Periode *", 
                        periode_options,
                        index=periode_index,
                        key="edit_periode"
                    )
                    
                    st.text_input(
                        "Tahun",
                        value=str(edit_tgl_mulai.year),
                        disabled=True,
                        key="edit_tahun"
                    )
            
            st.divider()
            
            # =============================
            # PREVIEW & SUBMIT
            # =============================
            with st.expander("👀 Preview Data Setelah Edit", expanded=False):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.write(f"**ID:** {edit_id_magang}")
                    st.write(f"**Nama:** {edit_nama}")
                    st.write(f"**Jenis Kelamin:** {edit_jenis_kelamin}")
                    st.write(f"**Jurusan:** {edit_jurusan}")
                    st.write(f"**Jenjang:** {edit_jenjang}")
                    st.write(f"**Sekolah:** {edit_sekolah}")
                with col_p2:
                    st.write(f"**Jenis Sekolah:** {edit_jenis_univ_sekolah}")
                    st.write(f"**Dept:** {edit_dept}")
                    st.write(f"**Subdept:** {edit_subdept}")
                    st.write(f"**Bulan:** {edit_durasi}")
                    st.write(f"**Periode:** {edit_periode}")
                    st.write(f"**Keterangan:** {edit_keterangan or '-'}")
                
                bulan_indo_list = [
                    "Januari","Februari","Maret","April","Mei","Juni",
                    "Juli","Agustus","September","Oktober","November","Desember"
                ]
                tgl_mulai_format = f"{edit_tgl_mulai.day} {bulan_indo_list[edit_tgl_mulai.month-1]} {edit_tgl_mulai.year}"
                tgl_akhir_format = f"{edit_tgl_akhir.day} {bulan_indo_list[edit_tgl_akhir.month-1]} {edit_tgl_akhir.year}"
                
                st.write(f"**Jadwal:** {tgl_mulai_format} - {tgl_akhir_format} ({edit_durasi} bulan)")
            
            # Tombol Update
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            
            with col_btn2:
                if st.button("💾 UPDATE DATA", use_container_width=True, type="primary", key="btn_update"):
                    # Validasi
                    if not all([edit_nama, edit_jurusan, edit_sekolah]):
                        st.error("❌ Semua field wajib harus diisi!")
                    else:
                        bulan_indo_list = [
                            "Januari","Februari","Maret","April","Mei","Juni",
                            "Juli","Agustus","September","Oktober","November","Desember"
                        ]
                        
                        tgl_mulai_format = f"{edit_tgl_mulai.day} {bulan_indo_list[edit_tgl_mulai.month-1]} {edit_tgl_mulai.year}"
                        tgl_akhir_format = f"{edit_tgl_akhir.day} {bulan_indo_list[edit_tgl_akhir.month-1]} {edit_tgl_akhir.year}"
                        
                        updated_data = {
                            'ID_Magang': edit_id_magang,
                            'Nama': edit_nama,
                            'Jenis Kelamin': edit_jenis_kelamin,
                            'Jurusan/Fakultas': edit_jurusan,
                            'Jenjang': edit_jenjang,
                            'Sekolah/Universitas': edit_sekolah,
                            'Jenis Univ/Sekolah': edit_jenis_univ_sekolah,
                            'Bagian/Dept': edit_dept,
                            'Sub Dept': edit_subdept,
                            'Bulan': edit_durasi,
                            'Mulai': tgl_mulai_format,
                            'Akhir': tgl_akhir_format,
                            'Periode': edit_periode,
                            'Tahun': edit_tgl_mulai.year,
                            'Keterangan': edit_keterangan,
                            'Catatan': selected_data.get('Catatan', '')
                        }
                        
                        with st.spinner("Mengupdate data..."):
                            if update_internship_data(edit_id_magang, updated_data):
                                st.session_state.edit_mode = False
                                st.session_state.selected_data = None
                                st.success("✅ Data berhasil diupdate!")
                                st.balloons()
                                
                                # Refresh data
                                refresh_data_in_session()
                                tm.sleep(2)
                                st.rerun()

# =========================
# HALAMAN STATUS PENDAFTARAN
# =========================
def halaman_Magang_Analytic():
    # Load data
    df = st.session_state.data_magang.copy()
    tab1, tab2 = st.tabs(["Dashboard", "Data Magang"])
    with tab1:
        st.title("Dashboard Analisis Data Magang")
        st.markdown("---")
        KPItotal_magang = len(df)
        KPIongoing = (df['S/A/SB/OP/DT'] == "On Going").sum()
        KPIuniversitas = (df['Jenis Univ/Sekolah'] == "Universitas").sum()
        KPIsekolah = (df["Jenis Univ/Sekolah"] == "Sekolah").sum()

        k1, k2, k3, k4 = st.columns(4)

        k1.metric("Total Peserta", KPItotal_magang)
        k2.metric("Magang Aktif", KPIongoing)
        k3.metric("Universitas", KPIuniversitas)
        k4.metric("Sekolah", KPIsekolah)
        
        st.markdown("---")
        
        
        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):

                status_counts = df['S/A/SB/OP/DT'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Jumlah']

                fig1 = px.pie(
                    status_counts,
                    values='Jumlah',
                    names='Status',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    title="Distribusi Status Magang"
                )
                fig1.update_traces(textposition='inside', textinfo='percent+label')
                fig1.update_layout(
                    title_x=0.3,
                    height=400
                )
                st.plotly_chart(fig1, use_container_width=True)

        with col2:
            with st.container(border=True):

                jk_counts = df['Jenis Kelamin'].value_counts().reset_index()
                jk_counts.columns = ['Jenis Kelamin', 'Jumlah']

                fig2 = px.pie(
                    jk_counts,
                    values='Jumlah',
                    names='Jenis Kelamin',
                    hole=0.4,
                    title="Proporsi Jenis Kelamin",
                    color='Jenis Kelamin',
                    color_discrete_map={
                        'Laki-laki': '#2E86AB',
                        'Perempuan': '#A23B72'
                    }
                )
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                fig2.update_layout(
                    title_x=0.3,
                    height=400
                )
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        # CHART SEKOLAH
        with col1:
            with st.container(border=True):

                df_sekolah = df[df['Jenis Univ/Sekolah'] == "Sekolah"]

                sekolah_counts = df_sekolah['Sekolah/Universitas'].value_counts().reset_index()
                sekolah_counts.columns = ['Sekolah', 'Jumlah']

                fig_sekolah = px.bar(
                    sekolah_counts,
                    y='Sekolah',
                    x='Jumlah',
                    orientation='h',
                    text='Jumlah',
                    color='Jumlah',
                    color_continuous_scale='Cividis',
                    title="Sekolah Pengirim Magang Terbanyak"
                )

                fig_sekolah.update_traces(
                    textposition='outside'
                )

                fig_sekolah.update_layout(
                    height=500,
                    yaxis={'categoryorder':'total ascending'},
                    title_x=0.3
                )

                st.plotly_chart(fig_sekolah, use_container_width=True)

        # CHART UNIVERSITAS
        with col2:
            with st.container(border=True):

                df_univ = df[df['Jenis Univ/Sekolah'] == "Universitas"]

                univ_counts = df_univ['Sekolah/Universitas'].value_counts().reset_index()
                univ_counts.columns = ['Universitas', 'Jumlah']

                fig_univ = px.bar(
                    univ_counts,
                    y='Universitas',
                    x='Jumlah',
                    orientation='h',
                    text='Jumlah',
                    color='Jumlah',
                    color_continuous_scale='Viridis',
                    title="Universitas Pengirim Magang Terbanyak"
                )

                fig_univ.update_traces(textposition='outside')

                fig_univ.update_layout(
                    height=500,
                    yaxis={'categoryorder':'total ascending'},
                    title_x=0.3
                )

                st.plotly_chart(fig_univ, use_container_width=True)

        st.markdown("---")

        #Visualisasi5
        col3, col4 = st.columns(2)
        with col3:
            with st.container(border=True):
                dept_counts = df['Bagian/Dept'].value_counts().reset_index()
                dept_counts.columns = ['Departemen', 'Jumlah']
                fig4 = px.bar(
                    dept_counts,
                    x='Departemen',
                    y='Jumlah',
                    color='Jumlah',
                    text='Jumlah',
                    color_continuous_scale='Plasma',
                    title="Jumlah Magang per Departemen"
                )
                fig4.update_traces(textposition='outside')
                fig4.update_layout(
                    height=450,
                    title_x=0.3,
                    xaxis_tickangle=-45
                )

                st.plotly_chart(fig4, use_container_width=True)

        with col4:
            with st.container(border=True):
                dept_status = pd.crosstab(df['Bagian/Dept'], df['S/A/SB/OP/DT'])
                dept_status_melted = dept_status.reset_index().melt(
                    id_vars='Bagian/Dept',
                    var_name='Status',
                    value_name='Jumlah'
                )
                fig5 = px.bar(
                    dept_status_melted,
                    x='Bagian/Dept',
                    y='Jumlah',
                    color='Status',
                    text='Jumlah',
                    barmode='stack',
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    title="Status Magang per Departemen"
                )
                fig5.update_traces(textposition='inside')
                fig5.update_layout(
                    height=450,
                    title_x=0.3,
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig5, use_container_width=True)

        st.markdown("---")

        # Visualisasi 6 dan 7 trend mulai magang dan akhir magang
        df['Mulai'] = df['Mulai'].apply(convert_tanggal)
        df['Akhir'] = df['Akhir'].apply(convert_tanggal)

        # TREND MULAI MAGANG
        df_mulai = df.dropna(subset=['Mulai']).copy()
        df_mulai['Bulan'] = df_mulai['Mulai'].dt.to_period('M')
        trend_mulai = (
            df_mulai
            .groupby('Bulan')
            .size()
            .reset_index(name='Jumlah')
        )
        trend_mulai['Bulan'] = trend_mulai['Bulan'].astype(str)

        # TREND AKHIR MAGANG
        df_akhir = df.dropna(subset=['Akhir']).copy()
        df_akhir['Bulan'] = df_akhir['Akhir'].dt.to_period('M')
        trend_akhir = (
            df_akhir
            .groupby('Bulan')
            .size()
            .reset_index(name='Jumlah')
        )
        trend_akhir['Bulan'] = trend_akhir['Bulan'].astype(str)

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                fig1 = px.line(
                    trend_mulai,
                    x='Bulan',
                    y='Jumlah',
                    markers=True,
                    title="Trend Mulai Magang per Bulan"
                )
                fig1.update_traces(
                    mode="lines+markers",
                    marker=dict(size=10),
                    line=dict(width=3)
                )
                fig1.update_layout(
                    title_x=0.3,
                    height=450,
                    xaxis_title="Bulan",
                    yaxis_title="Jumlah Peserta"
                )

                st.plotly_chart(fig1, use_container_width=True)

        with col2:
            with st.container(border=True):
                fig2 = px.line(
                    trend_akhir,
                    x='Bulan',
                    y='Jumlah',
                    markers=True,
                    title="Trend Akhir Magang per Bulan"
                )
                fig2.update_traces(
                    mode="lines+markers",
                    marker=dict(size=10),
                    line=dict(width=3)
                )
                fig2.update_layout(
                    title_x=0.3,
                    height=450,
                    xaxis_title="Bulan",
                    yaxis_title="Jumlah Peserta"
                )
                st.plotly_chart(fig2, use_container_width=True);
        
        st.markdown("---")
        
        #=== Visualisasi 8: Hierarki Sunburst Chart (Status - Departemen - Universitas) ===
        sunburst_data = df.groupby(['S/A/SB/OP/DT', 'Bagian/Dept', 'Sekolah/Universitas']).size().reset_index(name='Jumlah')
        fig10 = px.sunburst(sunburst_data, 
                        path=['S/A/SB/OP/DT', 'Bagian/Dept', 'Sekolah/Universitas'], 
                        values='Jumlah',
                        title='Hierarki: Status → Departemen → Universitas',
                        color='Jumlah',
                        color_continuous_scale='Viridis')
        fig10.update_layout(height=800, title_x=0.36)
        st.plotly_chart(fig10, use_container_width=True)
    
        st.markdown("---")

    with tab2:
        st.title("Data Magang")
        
        # ============================================
        # FILTER SECTION
        # ============================================
        with st.container(border=True):
            st.markdown("##### 🔍 Filter Data")
            
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                # Filter Nama (search)
                search_nama = st.text_input(
                    "Cari Nama",
                    placeholder="Masukkan nama...",
                    key="filter_nama_tab2"
                )
            
            with col_filter2:
                # Filter Bagian/Dept (multiselect)
                dept_options = ['Semua'] + sorted(df['Bagian/Dept'].unique().tolist())
                filter_dept = st.selectbox(
                    "Bagian/Dept",
                    options=dept_options,
                    key="filter_dept_tab2"
                )
            
            with col_filter3:
                # Filter Jenis Univ/Sekolah
                jenis_options = ['Semua', 'Universitas', 'Sekolah']
                filter_jenis = st.selectbox(
                    "Jenis Institusi",
                    options=jenis_options,
                    key="filter_jenis_tab2"
                )
        
        # ============================================
        # APPLY FILTERS
        # ============================================
        df_filtered = df.copy()
        
        # Filter berdasarkan Nama
        if search_nama:
            df_filtered = df_filtered[
                df_filtered['Nama'].astype(str).str.contains(search_nama, case=False, na=False)
            ]
        
        # Filter berdasarkan Departemen
        if filter_dept and filter_dept != 'Semua':
            df_filtered = df_filtered[df_filtered['Bagian/Dept'] == filter_dept]
        
        # Filter berdasarkan Jenis Institusi
        if filter_jenis and filter_jenis != 'Semua':
            df_filtered = df_filtered[df_filtered['Jenis Univ/Sekolah'] == filter_jenis]
        
        # ============================================
        # TAMPILKAN INFORMASI FILTER
        # ============================================
        st.markdown("---")
        
        # Info filter aktif
        filter_active = []
        if search_nama:
            filter_active.append(f"Nama mengandung '{search_nama}'")
        if filter_dept and filter_dept != 'Semua':
            filter_active.append(f"Dept: {filter_dept}")
        if filter_jenis and filter_jenis != 'Semua':
            filter_active.append(f"Jenis: {filter_jenis}")
        
        if filter_active:
            st.info(f"📊 Filter aktif: {', '.join(filter_active)} | Menampilkan {len(df_filtered)} dari {len(df)} data")
        else:
            st.info(f"📊 Total data: {len(df_filtered)}")
        
        # ============================================
        # TAMPILKAN DATAFRAME
        # ============================================
        if not df_filtered.empty:
            # Siapkan data untuk ditampilkan
            df_display = df_filtered.copy()
            
            # Konversi ID_Magang ke string jika ada
            if 'ID_Magang' in df_display.columns:
                df_display['ID_Magang'] = df_display['ID_Magang'].astype(str)
            
            # Tampilkan dataframe dengan styling
            st.dataframe(
                df_display,
                height=600,
                use_container_width=True,
                column_config={
                    "ID_Magang": "ID Magang",
                    "Nama": "Nama Lengkap",
                    "Jenis Kelamin": "JK",
                    "Jurusan/Fakultas": "Jurusan",
                    "Jenjang": "Jenjang",
                    "Sekolah/Universitas": "Institusi",
                    "Jenis Univ/Sekolah": "Jenis",
                    "Bagian/Dept": "Departemen",
                    "Sub Dept": "Sub Dept",
                    "Bulan": "Durasi",
                    "Mulai": "Tgl Mulai",
                    "Akhir": "Tgl Akhir",
                    "Periode": "Periode",
                    "Tahun": "Tahun",
                    "Keterangan": "Ket",
                    "Catatan": "Catatan",
                    "S/A/SB/OP/DT": "Status"
                }
            )
            
            # ============================================
            # STATISTIK CEPAT
            # ============================================
            st.divider()
            st.markdown("##### Statistik Data Terfilter")
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("Total Data", len(df_filtered))
            
            with col_stat2:
                if 'Jenis Kelamin' in df_filtered.columns:
                    laki = (df_filtered['Jenis Kelamin'] == 'Laki-laki').sum()
                    st.metric("Laki-laki", laki)
            
            with col_stat3:
                if 'Jenis Kelamin' in df_filtered.columns:
                    perempuan = (df_filtered['Jenis Kelamin'] == 'Perempuan').sum()
                    st.metric("Perempuan", perempuan)
            
            with col_stat4:
                if 'S/A/SB/OP/DT' in df_filtered.columns:
                    aktif = (df_filtered['S/A/SB/OP/DT'] == 'On Going').sum()
                    st.metric("Aktif", aktif)
            
            # ============================================
            # TOMBOL DOWNLOAD
            # ============================================
            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            with col_dl2:
                # Konversi ke CSV untuk download
                csv = df_display.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv,
                    file_name=f"data_magang_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_data_magang_csv"
                )
        else:
            st.warning("⚠️ Tidak ada data yang sesuai dengan filter")
            
            # Tampilkan data kosong dengan struktur kolom
            if df.empty:
                st.info("📭 Database magang kosong")
            else:
                st.info("📭 Coba atur ulang filter untuk melihat data")

# =========================
# HALAMAN DOKUMEN SAYA
# =========================
def halaman_Update_Presensi():
    tab11, tab22, tab33 = st.tabs(["Input Data Presensi", "Perbarui Data Presensi", "Data Presensi"])
    
    with tab11:
        st.title("🟢Sistem Input Data Presensi")
        st.markdown("**Ketentuan Upload File**")

        st.markdown("""
        1. File harus berformat **.xlsx** atau **.xls**  
        2. Kolom harus sesuai dengan format berikut
        """)

        st.markdown("**Kolom yang diperlukan:**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            - ID_Magang
            - Nama
            - Tanggal
            - Jam Masuk
            """)

        with col2:
            st.markdown("""
            - Jam Pulang
            - Scan Masuk
            - Scan Keluar
            - Terlambat
            """)

        with col3:
            st.markdown("""
            - Plg Cpt
            - Lembur
            - Jam Kerja
            - Jml Hadir
            """)
        
        st.markdown("---")

        # Load data dari Google Sheets
        db_data_presensi = load_data("data_presensi")
        db_magang = load_data("database_magang")

        upload_data_absen = st.file_uploader("Pilih file Excel", type=["xlsx", "xls"])

        # Inisialisasi session state
        if 'df_absen' not in st.session_state:
            st.session_state.df_absen = None
        if 'hasil_validasi' not in st.session_state:
            st.session_state.hasil_validasi = None

        # Jika ada file baru diupload
        if upload_data_absen is not None:
            df_absen = pd.read_excel(upload_data_absen)
            # Bersihkan nama kolom
            df_absen.columns = [str(col).strip() for col in df_absen.columns]

            # KONVERSI ID_Magang KE INTEGER (NaN jadi 0)
            if 'ID_Magang' in df_absen.columns:
                df_absen['ID_Magang'] = pd.to_numeric(df_absen['ID_Magang'], errors='coerce').fillna(0).astype(int)
                if (df_absen['ID_Magang'] == 0).any():
                    st.warning("⚠️ Beberapa ID_Magang tidak valid dan diganti 0. Harap periksa kembali data Anda.")

            st.session_state.df_absen = df_absen
            st.session_state.hasil_validasi = None  # reset hasil lama

        # Jika ada data di session state
        if st.session_state.df_absen is not None:
            df_absen = st.session_state.df_absen
            # Bersihkan nama kolom database (cukup sekali)
            db_data_presensi.columns = [str(col).strip() for col in db_data_presensi.columns]

            kolom_excel = list(df_absen.columns)
            kolom_database = list(db_data_presensi.columns)
            
            # Kolom yang dikecualikan dari pengecekan
            exclude_col = "Status Terbayar"
            kolom_database_tanpa_exclude = [col for col in kolom_database if col != exclude_col]

            if kolom_excel == kolom_database_tanpa_exclude:
                st.success("✅ Struktur kolom sesuai dengan database (tanpa kolom Status Terbayar)")
                st.write("Data yang diupload:")
                df_absen_tampil = df_absen.copy()
                df_absen_tampil["ID_Magang"] = df_absen_tampil["ID_Magang"].astype(str)
                st.dataframe(df_absen_tampil, use_container_width=True, height=200)

                # Validasi otomatis jika belum ada hasil
                if st.session_state.hasil_validasi is None:
                    with st.spinner("Memvalidasi data..."):
                        hasil = validasi_data(df_absen, db_magang, db_data_presensi)
                        st.session_state.hasil_validasi = hasil

                # Tampilkan hasil validasi
                hasil = st.session_state.hasil_validasi
                st.write(f"**Data valid:** {len(hasil['valid'])} baris")
                st.write(f"**Data gagal:** {len(hasil['gagal'])} baris")

                if hasil['gagal']:
                    st.error("Detail data gagal:")
                    df_gagal = pd.DataFrame(hasil['gagal'])
                    df_gagal_tampil = df_gagal.copy()
                    df_gagal_tampil["ID_Magang"] = df_gagal_tampil["ID_Magang"].astype(str)
                    st.dataframe(df_gagal_tampil)

                # Tombol simpan hanya jika ada data valid
                if hasil['valid']:
                    if st.button("Simpan Data Valid ke Database", type='primary'):
                        col_order = kolom_database  # urutan lengkap termasuk Status Terbayar
                        data_baru = []

                        for row_dict in hasil['valid']:
                            baris = []
                            for col in col_order:
                                if col == exclude_col:
                                    # Isi default untuk kolom yang dikecualikan
                                    val = ''
                                else:
                                    val = row_dict.get(col, '')
                                    # Tangani NaN
                                    if isinstance(val, float) and pd.isna(val):
                                        val = ''
                                    # Tangani datetime dan Timestamp
                                    elif isinstance(val, (datetime, pd.Timestamp)):
                                        val = val.strftime('%Y-%m-%d %H:%M:%S')
                                    # Tangani time (datetime.time)
                                    elif isinstance(val, time):
                                        val = val.strftime('%H:%M:%S')
                                    # Pastikan ID_Magang sebagai string
                                    if col == 'ID_Magang' and not isinstance(val, str):
                                        val = str(val) if val != '' else ''
                                baris.append(val)
                            data_baru.append(baris)

                        try:
                            append_to_sheet("data_presensi", data_baru)
                            st.success(f"✅ Berhasil menyimpan {len(data_baru)} data ke database.")
                            # Reset state agar tidak menyimpan ulang
                            st.session_state.hasil_validasi = None
                            st.session_state.df_absen = None
                            # Reload data untuk menampilkan yang terbaru
                            db_data_presensi = load_data("data_presensi")
                            refresh_data_in_session()
                            db_data_presensi.columns = [str(col).strip() for col in db_data_presensi.columns]
                            st.dataframe(db_data_presensi, use_container_width=True, height=200)
                        except Exception as e:
                            st.error(f"❌ Gagal menyimpan ke database: {e}")
            else:
                st.error("❌ Struktur kolom tidak sama dengan database (Status Terbayar dikecualikan)")
                # Hitung kolom yang hilang dan tambahan berdasarkan kolom_database_tanpa_exclude
                missing_columns = [col for col in kolom_database_tanpa_exclude if col not in kolom_excel]
                extra_columns = [col for col in kolom_excel if col not in kolom_database_tanpa_exclude]

                st.write("Kolom yang seharusnya ada di database (tanpa Status Terbayar):")
                st.write(kolom_database_tanpa_exclude)

                if missing_columns:
                    st.write("Kolom yang tidak ditemukan di file upload:")
                    st.write(missing_columns)

                if extra_columns:
                    st.write("Kolom tambahan di file upload:")
                    st.write(extra_columns)


    with tab22:
        st.title("🗑️ Hapus Data Presensi")
        st.markdown("**Hapus data presensi berdasarkan periode tanggal**")
        
        st.warning("""
        ⚠️ **PERHATIAN:**
        - Fitur ini akan **MENGHAPUS PERMANEN** data presensi
        - Data yang dihapus **TIDAK DAPAT DIKEMBALIKAN**
        - Harap periksa periode dengan teliti sebelum menghapus
        """)
        
        # Load data dari session state
        if 'data_presensi' in st.session_state:
            db_data_presensi = st.session_state.data_presensi
        else:
            db_data_presensi = load_data_cached("data_presensi")
        
        if 'data_magang' in st.session_state:
            db_magang = st.session_state.data_magang
        else:
            db_magang = load_data_cached("database_magang")
        
        # Tampilkan preview data yang ada
        with st.expander("📋 Preview Data Presensi Saat Ini", expanded=False):
            # Tampilkan sample data dengan format asli
            if not db_data_presensi.empty:
                sample_data = db_data_presensi.head(10).copy()
                if 'ID_Magang' in sample_data.columns:
                    sample_data['ID_Magang'] = sample_data['ID_Magang'].astype(str)
                st.dataframe(sample_data, use_container_width=True)
                st.caption(f"Total data: {len(db_data_presensi)} baris (menampilkan 10 sample)")
            else:
                st.info("Database presensi kosong")
        
        st.divider()
        
        # ============================================
        # INPUT PERIODE HAPUS
        # ============================================
        col1, col2 = st.columns(2)
        
        with col1:
            tgl_awal_hapus = st.date_input(
                "📅 Tanggal Awal Periode",
                value=datetime.now().date(),
                key="tgl_awal_hapus",
                format="DD/MM/YYYY"  # Streamlit akan menampilkan format ini
            )
        
        with col2:
            tgl_akhir_hapus = st.date_input(
                "📅 Tanggal Akhir Periode",
                value=datetime.now().date(),
                key="tgl_akhir_hapus",
                format="DD/MM/YYYY"
            )
        
        # Validasi tanggal
        if tgl_awal_hapus > tgl_akhir_hapus:
            st.error("❌ Tanggal awal harus lebih kecil atau sama dengan tanggal akhir!")
            st.stop()
        
        # ============================================
        # FILTER DATA UNTUK PREVIEW
        # ============================================
        if not db_data_presensi.empty:
            # Konversi kolom Tanggal dari format DD/MM/YYYY ke datetime
            db_data_presensi['Tanggal_dt'] = pd.to_datetime(
                db_data_presensi['Tanggal'], 
                format='%d/%m/%Y',  # FORMAT SESUAI: DD/MM/YYYY
                errors='coerce'
            )
            
            # Filter data berdasarkan periode
            mask = (
                (db_data_presensi['Tanggal_dt'] >= pd.Timestamp(tgl_awal_hapus)) &
                (db_data_presensi['Tanggal_dt'] <= pd.Timestamp(tgl_akhir_hapus))
            )
            
            data_terfilter = db_data_presensi.loc[mask].copy()
            jumlah_terfilter = len(data_terfilter)
            
            # Tampilkan informasi dengan format tanggal Indonesia
            tgl_awal_str = tgl_awal_hapus.strftime('%d/%m/%Y')
            tgl_akhir_str = tgl_akhir_hapus.strftime('%d/%m/%Y')
            
            st.info(f"📊 Ditemukan **{jumlah_terfilter}** data presensi pada periode **{tgl_awal_str} - {tgl_akhir_str}**")
            
            if jumlah_terfilter > 0:
                with st.expander("👀 Preview Data yang Akan Dihapus", expanded=True):
                    # Siapkan data untuk ditampilkan
                    data_preview = data_terfilter.copy()
                    
                    # Konversi ID_Magang ke string untuk tampilan
                    if 'ID_Magang' in data_preview.columns:
                        data_preview['ID_Magang'] = data_preview['ID_Magang'].astype(str)
                    
                    # Hapus kolom Tanggal_dt jika ada
                    if 'Tanggal_dt' in data_preview.columns:
                        data_preview = data_preview.drop(columns=['Tanggal_dt'])
                    
                    # Tampilkan sample (maks 50 baris)
                    if jumlah_terfilter > 50:
                        st.warning(f"Menampilkan 50 dari {jumlah_terfilter} data (terlalu banyak untuk ditampilkan)")
                        st.dataframe(data_preview.head(50), use_container_width=True)
                    else:
                        st.dataframe(data_preview, use_container_width=True)
                    
                    # Ringkasan per departemen (jika kolom tersedia)
                    if 'Bagian/Dept' in data_terfilter.columns:
                        dept_summary = data_terfilter['Bagian/Dept'].value_counts().reset_index()
                        dept_summary.columns = ['Departemen', 'Jumlah']
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write("**Ringkasan per Departemen:**")
                            st.dataframe(dept_summary, use_container_width=True)
                        
                        with col_b:
                            # Ringkasan per ID
                            id_summary = data_terfilter['ID_Magang'].value_counts().reset_index().head(10)
                            id_summary.columns = ['ID_Magang', 'Jumlah']
                            id_summary['ID_Magang'] = id_summary['ID_Magang'].astype(str)
                            st.write("**Top 10 ID Magang:**")
                            st.dataframe(id_summary, use_container_width=True)
                
                st.divider()
                
                # ============================================
                # KONFIRMASI DAN HAPUS
                # ============================================
                st.error(f"⚠️ **KONFIRMASI PENGHAPUSAN**")
                st.write(f"Anda akan menghapus **{jumlah_terfilter}** data presensi secara permanen!")
                st.write(f"Periode: **{tgl_awal_str} - {tgl_akhir_str}**")
                
                # Checkbox konfirmasi
                confirm1 = st.checkbox("Saya memahami bahwa data yang dihapus tidak dapat dikembalikan")
                confirm2 = st.checkbox(f"Saya yakin akan menghapus {jumlah_terfilter} data pada periode tersebut")
                
                # Input password untuk keamanan ekstra (opsional)
                st.caption("🔒 Untuk keamanan, masukkan password admin")
                password_confirm = st.text_input("Password:", type="password", key="password_hapus")
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                
                with col_btn2:
                    if st.button(
                        "🗑️ HAPUS DATA PERMANEN", 
                        use_container_width=True, 
                        type="primary",
                        disabled=not (confirm1 and confirm2 and password_confirm == "admin123")  # Ganti dengan password Anda
                    ):
                        
                        with st.spinner(f"Menghapus {jumlah_terfilter} data..."):
                            try:
                                # Panggil fungsi hapus berdasarkan periode
                                success, message, jumlah_hapus = hapus_data_by_periode(
                                    "data_presensi",
                                    tgl_awal_hapus,
                                    tgl_akhir_hapus
                                )
                                
                                if success:
                                    st.success(f"✅ **BERHASIL!** {message}")
                                    
                                    # Refresh data
                                    refresh_data_in_session()
                                    
                                    # Reset state
                                    st.balloons()
                                    tm.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Gagal menghapus data: {message}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
            else:
                st.success(f"✅ Tidak ada data pada periode {tgl_awal_str} - {tgl_akhir_str}")
        else:
            st.info("📭 Database presensi kosong")
        
    with tab33:
        st.title("📋 Data Presensi Saat Ini")
        
        # ============================================
        # FILTER PERIODE
        # ============================================
        with st.container(border=True):
            st.markdown("##### 📅 Filter Periode Tanggal")
            
            col_periode1, col_periode2, col_periode3 = st.columns([2, 2, 1])
            
            with col_periode1:
                # Tanggal Awal
                if 'filter_tgl_awal' not in st.session_state:
                    st.session_state.filter_tgl_awal = None
                
                tgl_awal_filter = st.date_input(
                    "Tanggal Awal",
                    value=None,
                    key="filter_tgl_awal_tab33",
                    format="DD/MM/YYYY"
                )
            
            with col_periode2:
                # Tanggal Akhir
                if 'filter_tgl_akhir' not in st.session_state:
                    st.session_state.filter_tgl_akhir = None
                
                tgl_akhir_filter = st.date_input(
                    "Tanggal Akhir",
                    value=None,
                    key="filter_tgl_akhir_tab33",
                    format="DD/MM/YYYY"
                )
            
            with col_periode3:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacer
                if st.button("🔄 Reset", use_container_width=True, key="reset_periode_tab33"):
                    st.session_state.filter_tgl_awal_tab33 = None
                    st.session_state.filter_tgl_akhir_tab33 = None
                    st.rerun()
        
        # ============================================
        # SIAPKAN DATA DENGAN KOLOM TANGGAL
        # ============================================
        # Copy data asli
        db_data_presensi_tampil = db_data_presensi.copy()
        
        # Konversi kolom Tanggal ke datetime untuk filtering
        if not db_data_presensi_tampil.empty and 'Tanggal' in db_data_presensi_tampil.columns:
            db_data_presensi_tampil['Tanggal_dt'] = pd.to_datetime(
                db_data_presensi_tampil['Tanggal'], 
                format='%d/%m/%Y', 
                errors='coerce'
            )
        
        # ============================================
        # APPLY FILTER PERIODE
        # ============================================
        df_filtered = db_data_presensi_tampil.copy()
        
        # Terapkan filter tanggal jika ada
        if tgl_awal_filter and tgl_akhir_filter:
            if tgl_awal_filter > tgl_akhir_filter:
                st.error("❌ Tanggal awal harus lebih kecil atau sama dengan tanggal akhir!")
            else:
                mask = (
                    (df_filtered['Tanggal_dt'] >= pd.Timestamp(tgl_awal_filter)) &
                    (df_filtered['Tanggal_dt'] <= pd.Timestamp(tgl_akhir_filter))
                )
                df_filtered = df_filtered.loc[mask].copy()
                
                # Tampilkan info periode
                tgl_awal_str = tgl_awal_filter.strftime('%d/%m/%Y')
                tgl_akhir_str = tgl_akhir_filter.strftime('%d/%m/%Y')
                st.info(f"📊 Menampilkan data periode **{tgl_awal_str} - {tgl_akhir_str}**")
        
        elif tgl_awal_filter or tgl_akhir_filter:
            st.warning("⚠️ Harap isi kedua tanggal awal dan akhir untuk filter periode")
        
        # ============================================
        # HAPUS KOLOM YANG TIDAK DITAMPILKAN
        # ============================================
        hidden_cols = ["Status Terbayar", "Tanggal_dt"]
        for col in hidden_cols:
            if col in df_filtered.columns:
                df_filtered = df_filtered.drop(columns=[col])
        
        # Konversi ID_Magang ke string
        if 'ID_Magang' in df_filtered.columns:
            df_filtered["ID_Magang"] = df_filtered["ID_Magang"].astype(str)
        
        # ============================================
        # TAMPILKAN INFORMASI DATA
        # ============================================
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.metric("Total Data", len(df_filtered))
        
        with col_info2:
            if not df_filtered.empty and 'ID_Magang' in df_filtered.columns:
                unique_mahasiswa = df_filtered['ID_Magang'].nunique()
                st.metric("Jumlah Mahasiswa", unique_mahasiswa)
        
        with col_info3:
            if not df_filtered.empty and 'Tanggal' in df_filtered.columns:
                # Hitung rentang tanggal
                try:
                    tanggal_dt = pd.to_datetime(df_filtered['Tanggal'], format='%d/%m/%Y', errors='coerce')
                    tgl_min = tanggal_dt.min().strftime('%d/%m/%Y') if pd.notna(tanggal_dt.min()) else '-'
                    tgl_max = tanggal_dt.max().strftime('%d/%m/%Y') if pd.notna(tanggal_dt.max()) else '-'
                    st.metric("Rentang Tanggal", f"{tgl_min} - {tgl_max}")
                except:
                    st.metric("Rentang Tanggal", "-")
        
        st.divider()
        
        # ============================================
        # TAMPILKAN DATAFRAME
        # ============================================
        if not df_filtered.empty:
            # Tampilkan dataframe dengan styling
            st.dataframe(
                df_filtered,
                height=600,
                use_container_width=True,
                column_config={
                    "ID_Magang": "ID Magang",
                    "Tanggal": "Tanggal",
                    "Jam Masuk": "Jam Masuk",
                    "Jam Pulang": "Jam Pulang",
                    "Scan Masuk": "Scan Masuk",
                    "Scan Keluar": "Scan Keluar",
                    "Terlambat": "Terlambat",
                    "Plg Cpt": "Pulang Cepat",
                    "Lembur": "Lembur",
                    "Jam Kerja": "Jam Kerja",
                    "Jml Hadir": "Jml Hadir"
                }
            )
            
            # ============================================
            # STATISTIK TAMBAHAN
            # ============================================
            with st.expander("📊 Statistik Tambahan", expanded=False):
                col_stat1, col_stat2 = st.columns(2)
                
                with col_stat1:
                    st.markdown("**Ringkasan per Mahasiswa**")
                    if 'ID_Magang' in df_filtered.columns:
                        mhs_summary = df_filtered.groupby('ID_Magang').size().reset_index()
                        mhs_summary.columns = ['ID Magang', 'Jumlah Kehadiran']
                        mhs_summary = mhs_summary.sort_values('Jumlah Kehadiran', ascending=False)
                        st.dataframe(mhs_summary, use_container_width=True, height=200)
                
                with col_stat2:
                    st.markdown("**Ringkasan per Bulan**")
                    if 'Tanggal' in df_filtered.columns:
                        # Ekstrak bulan dari tanggal
                        df_filtered['Bulan'] = pd.to_datetime(
                            df_filtered['Tanggal'], format='%d/%m/%Y', errors='coerce'
                        ).dt.month
                        
                        bulan_summary = df_filtered.groupby('Bulan').size().reset_index()
                        bulan_summary.columns = ['Bulan', 'Jumlah']
                        
                        # Mapping angka bulan ke nama bulan
                        nama_bulan = {
                            1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
                            7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
                        }
                        bulan_summary['Bulan'] = bulan_summary['Bulan'].map(nama_bulan)
                        
                        st.dataframe(bulan_summary, use_container_width=True, height=200)
                        
                        # Hapus kolom Bulan setelah digunakan
                        df_filtered = df_filtered.drop(columns=['Bulan'], errors='ignore')
            
            # ============================================
            # TOMBOL DOWNLOAD
            # ============================================
            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            with col_dl2:
                # Konversi ke CSV untuk download
                csv_data = df_filtered.to_csv(index=False).encode('utf-8')
                
                # Buat nama file dengan periode
                if tgl_awal_filter and tgl_akhir_filter:
                    periode_str = f"{tgl_awal_filter.strftime('%Y%m%d')}_{tgl_akhir_filter.strftime('%Y%m%d')}"
                else:
                    periode_str = "semua"
                
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv_data,
                    file_name=f"data_presensi_{periode_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_presensi_tab33"
                )
        else:
            st.warning("⚠️ Tidak ada data presensi pada periode yang dipilih")
            
            # Tampilkan pesan jika database kosong
            if db_data_presensi.empty:
                st.info("📭 Database presensi masih kosong")
            else:
                st.info("📭 Tidak ada data pada periode filter. Coba atur ulang filter.")


# =========================
# HALAMAN REKAPITULASI
# =========================
def halaman_Rekapitulasi_Presensi():
    tabb1, tabb2 = st.tabs(["Rekapitulasi", "Status Terbayar"])
    with tabb1:
        st.title("📊 Rekapitulasi Presensi dan UMUT Mahasiswa Magang")

        # ---------- SESSION STATE ----------
        if "rekap_ready" not in st.session_state:
            st.session_state.rekap_ready = False
        if "tgl_awal" not in st.session_state:
            st.session_state.tgl_awal = datetime.now().date()
        if "tgl_akhir" not in st.session_state:
            st.session_state.tgl_akhir = datetime.now().date()

        # ---------- INPUT PERIODE ----------
        col1, col2 = st.columns(2)

        with col1:
            tgl_awal = st.date_input("Tanggal Awal", value=st.session_state.tgl_awal)

        with col2:
            tgl_akhir = st.date_input("Tanggal Akhir", value=st.session_state.tgl_akhir)

        if tgl_awal > tgl_akhir:
            st.error("Tanggal awal harus lebih kecil atau sama dengan tanggal akhir.")
            return


        # ---------- TOMBOL PROSES ----------
        if st.button("🚀 Proses Rekapitulasi", use_container_width=True):

            st.session_state.rekap_ready = True
            st.session_state.tgl_awal = tgl_awal
            st.session_state.tgl_akhir = tgl_akhir

        # ---------- JIKA REKAP SUDAH DIPROSES ----------
        if st.session_state.rekap_ready:

            tgl_awal = st.session_state.tgl_awal
            tgl_akhir = st.session_state.tgl_akhir

            with st.spinner("Memuat data dari Google Sheets..."):
                try:
                    df_magang = st.session_state.data_magang.copy()
                    df_presensi = st.session_state.data_presensi.copy()
                except Exception as e:
                    st.error(f"Gagal memuat data: {e}")
                    return

            st.success("Data berhasil dimuat.")

            df_departemen = st.session_state.data_departemen.copy()

            try:
                df_departemen = st.session_state.data_departemen.copy()  # asumsikan sudah ada di session state

                istirahat_dict = {}
                for _, row in df_departemen.iterrows():
                    nama = row['nama_departemen']
                    mulai = parse_time(row['Mulai Istirahat'])
                    akhir = parse_time(row['Akhir Istirahat'])
                    if mulai is not None and akhir is not None:
                        istirahat_dict[nama] = (mulai, akhir)
                st.success("Data jam istirahat departemen berhasil dimuat.")
            except Exception as e:
                st.warning(f"Gagal memuat data jam istirahat: {e}. Menggunakan default (tanpa pengurangan).")
                istirahat_dict = {}

            # ---------- FILTER TANGGAL ----------
            df_presensi['Tanggal_dt'] = pd.to_datetime(
                df_presensi['Tanggal'], format='%d/%m/%Y', errors='coerce'
            )

            mask = (
                (df_presensi['Tanggal_dt'] >= pd.Timestamp(tgl_awal)) &
                (df_presensi['Tanggal_dt'] <= pd.Timestamp(tgl_akhir))
            )

            df_presensi_filter = df_presensi.loc[mask].copy()

            if df_presensi_filter.empty:
                st.warning("Tidak ada data presensi pada rentang tanggal tersebut.")
                return

            # ---------- MERGE ----------
            df_merged = pd.merge(
                df_presensi_filter,
                df_magang[['ID_Magang', 'Nama', 'Sub Dept', 'Bagian/Dept']],
                on='ID_Magang',
                how='left'
            )

            if 'Nama_x' in df_merged.columns and 'Nama_y' in df_merged.columns:
                df_merged['Nama'] = df_merged['Nama_y']
                df_merged.drop(columns=['Nama_x', 'Nama_y'], inplace=True)

            # ---------- DAFTAR TANGGAL ----------
            date_range = pd.date_range(start=tgl_awal, end=tgl_akhir)
            tanggal_list = [str(d.day) for d in date_range]

            # ---------- PERHITUNGAN ----------
            hasil = {}

            for id_magang, group in df_merged.groupby('ID_Magang'):

                nama = group['Nama'].iloc[0]
                sub_dept = group['Sub Dept'].iloc[0] if pd.notna(group['Sub Dept'].iloc[0]) else ''

                umut_per_tgl = {tgl: 0 for tgl in tanggal_list}
                keterangan_list = []

                for _, row in group.iterrows():
                    tgl = str(row['Tanggal_dt'].day)
                    if tgl not in umut_per_tgl:
                        continue

                    dept = row.get('Bagian/Dept')
                    if dept in istirahat_dict:
                        break_start, break_end = istirahat_dict[dept]
                    else:
                        break_start, break_end = None, None

                    umut, ket = hitung_umut(row, break_start=break_start, break_end=break_end)

                    umut_per_tgl[tgl] = umut
                    if ket:
                        keterangan_list.append(f"Tgl {tgl} {ket}")

                total = sum(umut_per_tgl.values())
                keterangan = "; ".join(keterangan_list)

                hasil[id_magang] = {
                    'ID_Magang': id_magang,
                    'Nama': nama,
                    'Sub Dept': sub_dept,
                    **umut_per_tgl,
                    'Pendapatan': total,
                    'Keterangan': keterangan
                }

            # ---------- DATAFRAME HASIL ----------
            df_hasil = pd.DataFrame.from_dict(hasil, orient='index')

            kolom_tanggal = [str(t) for t in tanggal_list]

            kolom_akhir = (
                ['ID_Magang', 'Nama', 'Sub Dept'] +
                kolom_tanggal +
                ['Pendapatan', 'Keterangan']
            )

            df_hasil = df_hasil[kolom_akhir]

            st.subheader(f"📋 Rekap UMUT per Departemen Periode {tgl_awal} hingga {tgl_akhir}")

            # ---------- TAMBAH DEPARTEMEN ----------
            df_dept = df_magang[['ID_Magang', 'Bagian/Dept']].drop_duplicates()

            df_hasil_with_dept = df_hasil.merge(df_dept, on='ID_Magang', how='left')

            dept_list = df_hasil_with_dept['Bagian/Dept'].dropna().unique()

            if len(dept_list) == 0:
                st.warning("Tidak ada data mahasiswa dengan departemen.")
                return

            tabs = st.tabs([f"🏢 {dept}" for dept in dept_list])

            periode_str = f"Periode: {tgl_awal.strftime('%d/%m/%Y')} - {tgl_akhir.strftime('%d/%m/%Y')}"

            for i, (tab, dept) in enumerate(zip(tabs, dept_list)):

                with tab:

                    df_tab = df_hasil_with_dept[
                        df_hasil_with_dept['Bagian/Dept'] == dept
                    ].drop(columns=['Bagian/Dept'])

                    st.dataframe(df_tab)

                    clm1, clm2, clm3 = st.columns(3)

                    # ---------- TOTAL ----------
                    with clm1:

                        total_pendapatan = df_tab['Pendapatan'].sum()

                        st.metric(
                            "💰 Total Pendapatan Departemen",
                            f"Rp {total_pendapatan:,.0f}"
                        )

                    # ---------- DOWNLOAD ----------
                    st.divider()
                    output_all = BytesIO()
                    with pd.ExcelWriter(output_all, engine='xlsxwriter') as writer:
                        for dept_dl in dept_list:
                            df_tab_dl = df_hasil_with_dept[df_hasil_with_dept['Bagian/Dept'] == dept_dl].drop(columns=['Bagian/Dept'])
                            judul = f"Rekap UMUT - Departemen {dept_dl}\n{periode_str}"
                            sheet_name = dept_dl[:31]
                            create_excel_sheet(writer, df_tab_dl, sheet_name, judul)
                    output_all.seek(0)
                    st.download_button(
                        label="📥 Download Excel Semua Departemen",
                        data = output_all,
                        file_name = f"rekap_umut_semua_{tgl_awal.strftime('%Y%m%d')}_{tgl_akhir.strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key=f"download_rekap_umut_{i}_{dept}"
                    )

                    # ---------- TANDAI TERBAYAR ----------
                    # ---------- TANDAI TERBAYAR (VERSI DENGAN FILTER SCAN TIDAK KOSONG) ----------
                    with clm3:
                        with st.popover(f"✅ Tandai {dept} Terbayar"):
                            # Identifikasi data dengan UMUT > 0
                            data_terbayar = []
                            
                            for _, row in df_tab.iterrows():
                                id_magang = row['ID_Magang']
                                
                                # Loop melalui kolom tanggal
                                for tgl in kolom_tanggal:
                                    umut = row[tgl]
                                    
                                    # Cek data presensi untuk tanggal ini
                                    tgl_int = int(tgl)
                                    tgl_filter = date_range[date_range.day == tgl_int]
                                    
                                    if len(tgl_filter) > 0:
                                        tgl_target = tgl_filter[0]
                                        
                                        # Cari data presensi untuk ID dan tanggal ini
                                        data_scan = df_presensi_filter[
                                            (df_presensi_filter['ID_Magang'] == id_magang) & 
                                            (df_presensi_filter['Tanggal_dt'].dt.date == tgl_target.date())
                                        ]
                                        
                                        # Jika UMUT > 0, tandai sebagai terbayar TANPA memeriksa scan
                                        if umut > 0:
                                            # Ambil data scan jika ada (untuk informasi saja)
                                            scan_masuk = ''
                                            scan_keluar = ''
                                            scan_masuk_valid = False
                                            scan_keluar_valid = False
                                            
                                            if not data_scan.empty:
                                                row_scan = data_scan.iloc[0]
                                                scan_masuk = row_scan.get('Scan Masuk', '')
                                                scan_keluar = row_scan.get('Scan Keluar', '')
                                                scan_masuk_valid = not pd.isna(scan_masuk) and str(scan_masuk).strip() != ''
                                                scan_keluar_valid = not pd.isna(scan_keluar) and str(scan_keluar).strip() != ''
                                            
                                            data_terbayar.append({
                                                'ID_Magang': id_magang,
                                                'Tanggal': tgl,
                                                'Tanggal_full': tgl_target.strftime('%d/%m/%Y'),
                                                'UMUT': umut,
                                                'Scan Masuk': scan_masuk,
                                                'Scan Keluar': scan_keluar,
                                                'Scan_Masuk_Valid': scan_masuk_valid,
                                                'Scan_Keluar_Valid': scan_keluar_valid
                                            })
                            
                            df_terbayar = pd.DataFrame(data_terbayar)
                            total_terbayar = len(df_terbayar)
                            
                            # Hitung statistik untuk ditampilkan
                            total_umut_positif = 0
                            total_scan_lengkap = 0
                            total_scan_hanya_masuk = 0
                            total_scan_hanya_keluar = 0
                            total_scan_kosong = 0
                            
                            for _, row in df_terbayar.iterrows():
                                total_umut_positif += 1
                                
                                scan_masuk_valid = row.get('Scan_Masuk_Valid', False)
                                scan_keluar_valid = row.get('Scan_Keluar_Valid', False)
                                
                                if scan_masuk_valid and scan_keluar_valid:
                                    total_scan_lengkap += 1
                                elif scan_masuk_valid and not scan_keluar_valid:
                                    total_scan_hanya_masuk += 1
                                elif not scan_masuk_valid and scan_keluar_valid:
                                    total_scan_hanya_keluar += 1
                                else:
                                    total_scan_kosong += 1
                            
                            # Tampilkan peringatan dengan detail
                            warning_message = (
                                f"Anda akan menandai presensi mahasiswa **{dept}** pada periode "
                                f"{tgl_awal.strftime('%d/%m/%Y')} - {tgl_akhir.strftime('%d/%m/%Y')} "
                                f"sebagai **terbayar**.\n\n"
                                f"⚠️ **Peringatan:** Data akan ditandai terbayar MESKIPUN scan tidak lengkap.\n"
                                f"Tindakan ini tidak dapat dibatalkan. Harap perbaiki data presensi jika ada CICO"
                            )
                            
                            st.warning(warning_message)
                            
                            if st.button("Ya, tandai sekarang", key=f"confirm_bayar_{i}_{dept}"):
                                if total_terbayar == 0:
                                    st.warning("⚠️ Tidak ada data dengan UMUT > 0 pada periode ini.")
                                else:
                                    st.info(f"Memproses update {total_terbayar} data ke Google Sheets...")
                                    
                                    try:
                                        # Gunakan fungsi dari utils.py
                                        worksheet_presensi = get_worksheet("data_presensi")
                                        if not worksheet_presensi:
                                            st.error("❌ Gagal mengakses sheet data_presensi.")
                                            return
                                        
                                        # Ambil semua data
                                        all_values = worksheet_presensi.get_all_values()
                                        if len(all_values) == 0:
                                            st.warning("⚠️ Sheet data_presensi kosong.")
                                            return
                                        
                                        headers = all_values[0]
                                        
                                        # Cari indeks kolom yang diperlukan
                                        required_columns = ['ID_Magang', 'Tanggal', 'Status Terbayar']
                                        column_indices = {}
                                        
                                        for col in required_columns:
                                            try:
                                                column_indices[col] = headers.index(col)
                                            except ValueError:
                                                st.error(f"❌ Kolom '{col}' tidak ditemukan di sheet data_presensi.")
                                                return
                                        
                                        # Buat lookup set untuk data yang akan ditandai (ID + Tanggal)
                                        lookup_set = set()
                                        for _, row in df_terbayar.iterrows():
                                            id_m = str(row['ID_Magang']).strip()
                                            tgl_full = row['Tanggal_full']  # Format DD/MM/YYYY
                                            lookup_set.add((id_m, tgl_full))
                                        
                                        # Siapkan updates dalam format batch
                                        updates = []
                                        updated_count = 0
                                        not_found_count = 0
                                        
                                        # Loop melalui baris data di sheet
                                        for i, row in enumerate(all_values[1:], start=2):
                                            if len(row) <= max(column_indices.values()):
                                                continue
                                            
                                            id_m = str(row[column_indices['ID_Magang']]).strip()
                                            tgl_str = row[column_indices['Tanggal']].strip()
                                            
                                            # Cek apakah kombinasi ID + Tanggal ada di lookup_set
                                            if (id_m, tgl_str) in lookup_set:
                                                # HAPUS VALIDASI SCAN - LANGSUNG UPDATE TANPA MEMERIKSA SCAN
                                                col_letter = gspread.utils.rowcol_to_a1(1, column_indices['Status Terbayar'] + 1)[0]
                                                cell_range = f"{col_letter}{i}"
                                                updates.append({
                                                    'range': cell_range,
                                                    'values': [['terbayar']]
                                                })
                                                updated_count += 1
                                        
                                        if updates:
                                            # Lakukan batch update ke Google Sheets
                                            with st.spinner(f"🔄 Mengupdate {len(updates)} data..."):
                                                # Split updates menjadi batch yang lebih kecil jika perlu (maks 100 per batch)
                                                batch_size = 100
                                                for j in range(0, len(updates), batch_size):
                                                    batch = updates[j:j+batch_size]
                                                    worksheet_presensi.batch_update(batch)
                                            
                                            # Tampilkan ringkasan hasil
                                            st.success(f"✅ Berhasil menandai {updated_count} baris presensi sebagai TERBAYAR di departemen {dept}.")
                                            
                                            # Tampilkan detail statistik scan
                                            st.info(
                                                f"📊 **Rincian data yang ditandai:**\n\n"
                                                f"• Scan lengkap: {total_scan_lengkap} data\n"
                                                f"• Scan hanya masuk: {total_scan_hanya_masuk} data\n"
                                                f"• Scan hanya keluar: {total_scan_hanya_keluar} data\n"
                                                f"• Scan kosong: {total_scan_kosong} data"
                                            )
                                            
                                            if updated_count < total_terbayar:
                                                not_found = total_terbayar - updated_count
                                                st.warning(f"⚠️ {not_found} data tidak ditemukan di database presensi.")
                                            
                                            # Refresh data di session state
                                            if refresh_data_in_session():
                                                st.success("📊 Data berhasil direfresh!")
                                                st.rerun()
                                            else:
                                                st.warning("⚠️ Data berhasil diupdate, tapi gagal refresh cache. Silakan refresh manual.")
                                        else:
                                            st.warning("⚠️ Tidak ada baris presensi yang cocok dengan kriteria atau semua data sudah terbayar.")
                                            
                                    except gspread.exceptions.APIError as e:
                                        st.error(f"❌ Error API Google Sheets: {str(e)}")
                                        st.info("💡 Coba refresh halaman dan ulangi beberapa saat lagi.")
                                    except Exception as e:
                                        st.error(f"❌ Terjadi error: {str(e)}")
                                        st.exception(e)  # Untuk debugging, hapus di production

        # ---------- KALKULATOR WAKTU (TAMBAHAN) ----------
    with st.container(border=True):
        st.markdown("<b>Kalkulator Waktu</b>", unsafe_allow_html=True)
        kolum1, kolum2, kolum3, kolum4 = st.columns(4)
        with kolum1:
            jam_mulai = st.text_input("Jam Mulai (HH:MM)", "08:00")
        with kolum2:
            jam_akhir = st.text_input("Jam Akhir (HH:MM)", "17:00")

        with kolum3:
            if st.button("Hitung Durasi"):
                try:
                    t1 = datetime.strptime(jam_mulai, "%H:%M")
                    t2 = datetime.strptime(jam_akhir, "%H:%M")
                    durasi = t2 - t1
                    total_detik = durasi.total_seconds()
                    jam = int(total_detik // 3600)
                    menit = int((total_detik % 3600) // 60)
                    st.success(f"Durasi kerja: {jam} jam {menit} menit")
                except:
                    st.error("Format jam harus HH:MM (contoh 08:30)")
    
    with tabb2:
        st.title("💰 Rekapitulasi UMUT Terbayar")
        st.markdown("Menampilkan data presensi yang sudah ditandai **terbayar** berdasarkan periode dan status pembayaran")
        
        # Load data dari session state atau langsung dari cache
        if 'data_presensi' in st.session_state:
            df_presensi = st.session_state.data_presensi.copy()
        else:
            df_presensi = load_data_cached("data_presensi")
        
        if 'data_magang' in st.session_state:
            df_magang = st.session_state.data_magang.copy()
        else:
            df_magang = load_data_cached("database_magang")
        
        # ============================================
        # FILTER UTAMA
        # ============================================
        with st.container(border=True):
            st.subheader("🔍 Filter Data")
            
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                # Filter berdasarkan status terbayar
                status_options = ["Semua Status", "Terbayar", "Belum Terbayar"]
                filter_status = st.selectbox(
                    "Status Pembayaran",
                    options=status_options,
                    index=1,  # Default ke "Terbayar"
                    key="filter_status_terbayar"
                )
            
            with col_f2:
                # Filter berdasarkan departemen
                dept_options = ["Semua Departemen"] + sorted(df_magang['Bagian/Dept'].unique().tolist())
                filter_dept = st.selectbox(
                    "Departemen",
                    options=dept_options,
                    key="filter_dept_terbayar"
                )
            
            with col_f3:
                # Filter berdasarkan periode tanggal
                if not df_presensi.empty and 'Tanggal' in df_presensi.columns:
                    # Konversi tanggal untuk range
                    df_presensi['Tanggal_dt_filter'] = pd.to_datetime(
                        df_presensi['Tanggal'], format='%d/%m/%Y', errors='coerce'
                    )
                    min_date = df_presensi['Tanggal_dt_filter'].min().date() if not df_presensi['Tanggal_dt_filter'].isna().all() else datetime.now().date()
                    max_date = df_presensi['Tanggal_dt_filter'].max().date() if not df_presensi['Tanggal_dt_filter'].isna().all() else datetime.now().date()
                else:
                    min_date = datetime.now().date()
                    max_date = datetime.now().date()
                
                filter_tanggal = st.date_input(
                    "Periode Tanggal",
                    value=(min_date, max_date),
                    key="filter_tanggal_terbayar"
                )
        
        # ============================================
        # PREPARE DATA
        # ============================================
        if not df_presensi.empty:
            # Konversi tanggal untuk filtering
            df_presensi['Tanggal_dt'] = pd.to_datetime(
                df_presensi['Tanggal'], format='%d/%m/%Y', errors='coerce'
            )
            
            # Merge dengan data magang untuk mendapatkan departemen
            df_display = pd.merge(
                df_presensi,
                df_magang[['ID_Magang', 'Nama', 'Bagian/Dept', 'Sub Dept']],
                on='ID_Magang',
                how='left'
            )
            
            # ============================================
            # APLIKASIKAN FILTER
            # ============================================
            
            # Filter status
            if filter_status == "Terbayar":
                df_display = df_display[df_display['Status Terbayar'].str.lower() == 'terbayar']
            elif filter_status == "Belum Terbayar":
                df_display = df_display[
                    df_display['Status Terbayar'].isna() | 
                    (df_display['Status Terbayar'] == '') | 
                    (df_display['Status Terbayar'].str.lower() != 'terbayar')
                ]
            
            # Filter departemen
            if filter_dept != "Semua Departemen":
                df_display = df_display[df_display['Bagian/Dept'] == filter_dept]
            
            # Filter tanggal
            if len(filter_tanggal) == 2:
                tgl_mulai, tgl_selesai = filter_tanggal
                df_display = df_display[
                    (df_display['Tanggal_dt'] >= pd.Timestamp(tgl_mulai)) &
                    (df_display['Tanggal_dt'] <= pd.Timestamp(tgl_selesai))
                ]
            
            # ============================================
            # METRIKS RINGKASAN
            # ============================================
            st.divider()
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                total_data = len(df_display)
                st.metric("📊 Total Data", f"{total_data} baris")
            
            with col_m2:
                total_mahasiswa = df_display['ID_Magang'].nunique()
                st.metric("👥 Jumlah Mahasiswa", total_mahasiswa)
            
            with col_m3:
                if filter_status == "Terbayar":
                    total_terbayar = len(df_display)
                else:
                    total_terbayar = len(df_display[df_display['Status Terbayar'].str.lower() == 'terbayar'])
                st.metric("✅ Sudah Terbayar", total_terbayar)
            
            with col_m4:
                if filter_status == "Belum Terbayar":
                    total_belum = len(df_display)
                else:
                    total_belum = len(df_display[
                        df_display['Status Terbayar'].isna() | 
                        (df_display['Status Terbayar'] == '') | 
                        (df_display['Status Terbayar'].str.lower() != 'terbayar')
                    ])
                st.metric("⏳ Belum Terbayar", total_belum)
            
            st.divider()
            
            # ============================================
            # TABEL DATA
            # ============================================
            if not df_display.empty:
                # Siapkan kolom untuk ditampilkan
                display_columns = ['ID_Magang', 'Nama', 'Bagian/Dept', 'Sub Dept', 
                                'Tanggal', 'Jam Masuk', 'Jam Pulang', 
                                'Scan Masuk', 'Scan Keluar', 'Status Terbayar']
                
                # Filter kolom yang ada
                available_columns = [col for col in display_columns if col in df_display.columns]
                df_show = df_display[available_columns].copy()
                
                # Konversi ID_Magang ke string untuk tampilan
                if 'ID_Magang' in df_show.columns:
                    df_show['ID_Magang'] = df_show['ID_Magang'].astype(str)
                
                # Beri warna pada status terbayar
                def color_status(val):
                    if pd.isna(val) or val == '':
                        return 'background-color: #ffcccc'  # Merah muda untuk belum terbayar
                    elif str(val).lower() == 'terbayar':
                        return 'background-color: #ccffcc'  # Hijau muda untuk sudah terbayar
                    return ''
                
                if 'data_magang' in st.session_state:
                    df_magang = st.session_state.data_magang.copy()
                    # Buat mapping ID_Magang ke Nama
                    mapping_nama = dict(zip(df_magang['ID_Magang'].astype(str), df_magang['Nama']))
                    mapping_dept = dict(zip(df_magang['ID_Magang'].astype(str), df_magang['Bagian/Dept']))
                    mapping_subdept = dict(zip(df_magang['ID_Magang'].astype(str), df_magang['Sub Dept']))
                    
                    # Tambahkan kolom Nama ke df_show jika belum ada
                    if 'Nama' not in df_show.columns:
                        df_show['Nama'] = df_show['ID_Magang'].astype(str).map(mapping_nama).fillna('-')
                    
                    # Reorder columns untuk menampilkan Nama di awal
                    cols = df_show.columns.tolist()
                    if 'Nama' in cols:
                        # Pindahkan ID_Magang dan Nama ke depan
                        cols.insert(0, cols.pop(cols.index('Nama')))
                        cols.insert(0, cols.pop(cols.index('ID_Magang')))
                        df_show = df_show[cols]
                else:
                    st.warning("⚠️ Data database magang tidak ditemukan. Nama mahasiswa tidak dapat ditampilkan.")
                    mapping_nama = {}
                    mapping_dept = {}
                    mapping_subdept = {}

                # Tampilkan dataframe dengan styling
                st.dataframe(
                    df_show.style.applymap(color_status, subset=['Status Terbayar'] if 'Status Terbayar' in df_show.columns else []),
                    use_container_width=True,
                    height=400
                )
                
                # ============================================
                # REKAPITULASI PER MAHASISWA
                # ============================================
                st.divider()
                st.subheader("📊 Rekapitulasi per Mahasiswa")

                # Ambil data nama dari database_magang berdasarkan ID_Magang
                if 'data_magang' in st.session_state and not st.session_state.data_magang.empty:
                    df_magang = st.session_state.data_magang.copy()
                    
                    # Buat dictionary mapping ID_Magang ke Nama
                    mapping_nama = dict(zip(df_magang['ID_Magang'].astype(str), df_magang['Nama']))
                    mapping_dept = dict(zip(df_magang['ID_Magang'].astype(str), df_magang['Bagian/Dept']))
                    mapping_subdept = dict(zip(df_magang['ID_Magang'].astype(str), df_magang['Sub Dept']))
                else:
                    st.warning("⚠️ Data database magang tidak ditemukan")
                    mapping_nama = {}
                    mapping_dept = {}
                    mapping_subdept = {}

                # Hitung statistik per mahasiswa
                rekap_mahasiswa = []
                for id_mhs, group in df_display.groupby('ID_Magang'):
                    id_mhs_str = str(id_mhs)
                    
                    # Ambil nama dari mapping (database magang)
                    nama = mapping_nama.get(id_mhs_str, '-')
                    dept = mapping_dept.get(id_mhs_str, '-')
                    subdept = mapping_subdept.get(id_mhs_str, '-')
                    
                    total_hadir = len(group)
                    
                    # Hitung status terbayar
                    if 'Status Terbayar' in group.columns:
                        total_terbayar = len(group[group['Status Terbayar'].astype(str).str.lower() == 'terbayar'])
                    else:
                        total_terbayar = 0
                    
                    total_belum = total_hadir - total_terbayar
                    
                    rekap_mahasiswa.append({
                        'ID_Magang': id_mhs_str,
                        'Nama': nama,
                        'Departemen': dept,
                        'Sub Dept': subdept,
                        'Total Hadir': total_hadir,
                        'Sudah Terbayar': total_terbayar,
                        'Belum Terbayar': total_belum,
                        'Persentase Terbayar': f"{(total_terbayar/total_hadir*100):.1f}%" if total_hadir > 0 else "0%"
                    })

                df_rekap = pd.DataFrame(rekap_mahasiswa)

                # Tampilkan dataframe
                st.dataframe(df_rekap, use_container_width=True, height=300)

                # Debug: Cek ID yang tidak ditemukan
                missing_ids = [id_mhs_str for id_mhs_str in df_display['ID_Magang'].astype(str).unique() if id_mhs_str not in mapping_nama]
                if missing_ids:
                    with st.expander("🔍 ID Magang yang tidak ditemukan di database"):
                        st.write(f"Jumlah ID tidak ditemukan: {len(missing_ids)}")
                        st.write("Contoh ID:", missing_ids[:10])
                        
                # ============================================
                # VISUALISASI
                # ============================================
                st.divider()
                st.subheader("📈 Visualisasi Status Terbayar")
                
                col_v1, col_v2 = st.columns(2)
                
                with col_v1:
                    # Pie chart status terbayar keseluruhan
                    status_counts = df_display['Status Terbayar'].fillna('Belum Terbayar').replace('', 'Belum Terbayar')
                    status_counts = status_counts.apply(lambda x: 'Terbayar' if str(x).lower() == 'terbayar' else 'Belum Terbayar')
                    status_data = status_counts.value_counts().reset_index()
                    status_data.columns = ['Status', 'Jumlah']
                    
                    fig_pie = px.pie(
                        status_data,
                        values='Jumlah',
                        names='Status',
                        title="Proporsi Status Terbayar",
                        color='Status',
                        color_discrete_map={
                            'Terbayar': '#4CAF50',
                            'Belum Terbayar': '#FF5722'
                        },
                        hole=0.4
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_v2:
                    # Bar chart per departemen
                    dept_status = df_display.copy()
                    dept_status['Status'] = dept_status['Status Terbayar'].fillna('Belum Terbayar').replace('', 'Belum Terbayar')
                    dept_status['Status'] = dept_status['Status'].apply(lambda x: 'Terbayar' if str(x).lower() == 'terbayar' else 'Belum Terbayar')
                    
                    dept_summary = dept_status.groupby(['Bagian/Dept', 'Status']).size().reset_index(name='Jumlah')
                    
                    fig_bar = px.bar(
                        dept_summary,
                        x='Bagian/Dept',
                        y='Jumlah',
                        color='Status',
                        title="Status Terbayar per Departemen",
                        color_discrete_map={
                            'Terbayar': '#4CAF50',
                            'Belum Terbayar': '#FF5722'
                        },
                        barmode='stack',
                        text='Jumlah'
                    )
                    fig_bar.update_traces(textposition='inside')
                    fig_bar.update_layout(
                        height=400,
                        xaxis_tickangle=-45,
                        xaxis_title="Departemen",
                        yaxis_title="Jumlah Data"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # ============================================
                # EXPORT DATA
                # ============================================
                st.divider()
                
                col_e1, col_e2, col_e3 = st.columns(3)
                
                with col_e1:
                    # Download data detail
                    output_detail = BytesIO()
                    with pd.ExcelWriter(output_detail, engine='xlsxwriter') as writer:
                        df_show.to_excel(writer, sheet_name='Detail Presensi', index=False)
                        
                        # Tambahkan sheet rekap
                        df_rekap.to_excel(writer, sheet_name='Rekap Mahasiswa', index=False)
                        
                        # Format excel
                        workbook = writer.book
                        worksheet1 = writer.sheets['Detail Presensi']
                        worksheet2 = writer.sheets['Rekap Mahasiswa']
                        
                        # Atur lebar kolom
                        for i, col in enumerate(df_show.columns):
                            max_len = max(df_show[col].astype(str).map(len).max(), len(col)) + 2
                            worksheet1.set_column(i, i, max_len)
                        
                        for i, col in enumerate(df_rekap.columns):
                            max_len = max(df_rekap[col].astype(str).map(len).max(), len(col)) + 2
                            worksheet2.set_column(i, i, max_len)
                    
                    output_detail.seek(0)
                    
                    st.download_button(
                        label="📥 Download Data Detail (Excel)",
                        data=output_detail,
                        file_name=f"status_terbayar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_status_terbayar"
                    )
                
                with col_e2:
                    # Tombol untuk menandai semua sebagai terbayar
                    if filter_status != "Terbayar" and len(df_display) > 0:
                        with st.popover("✅ Tandai Semua Terbayar"):
                            st.warning(
                                f"Anda akan menandai **{len(df_display)} data** sebagai **terbayar**. "
                                f"Tindakan ini akan mengupdate kolom Status Terbayar di Google Sheets. "
                                f"Proses ini tidak dapat dibatalkan."
                            )
                            
                            if st.button("Ya, tandai semua terbayar", key="confirm_bayar_semua"):
                                st.info("Memproses update ke Google Sheets...")
                                
                                try:
                                    # Buka koneksi ke Google Sheets
                                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                                    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                                    client = gspread.authorize(creds)
                                    spreadsheet = client.open_by_key(SPREADSHEET_ID)
                                    worksheet_presensi = spreadsheet.worksheet("data_presensi")
                                    
                                    # Ambil semua data
                                    all_values = worksheet_presensi.get_all_values()
                                    if len(all_values) == 0:
                                        st.warning("Sheet data_presensi kosong.")
                                        return
                                    
                                    headers = all_values[0]
                                    
                                    # Cari indeks kolom
                                    try:
                                        id_col_idx = headers.index('ID_Magang')
                                        tgl_col_idx = headers.index('Tanggal')
                                        status_col_idx = headers.index('Status Terbayar')
                                    except ValueError as e:
                                        st.error(f"Kolom wajib tidak ditemukan: {e}")
                                        return
                                    
                                    # Buat set kombinasi ID + Tanggal dari df_display
                                    update_set = set()
                                    for _, row in df_display.iterrows():
                                        id_m = str(row['ID_Magang'])
                                        tgl = row['Tanggal']
                                        update_set.add((id_m, tgl))
                                    
                                    updates = []
                                    for i, row in enumerate(all_values[1:], start=2):
                                        if len(row) <= max(id_col_idx, tgl_col_idx):
                                            continue
                                        id_m = str(row[id_col_idx]).strip()
                                        tgl_str = row[tgl_col_idx].strip()
                                        
                                        if (id_m, tgl_str) in update_set:
                                            col_letter = gspread.utils.rowcol_to_a1(1, status_col_idx + 1)[0]
                                            cell_range = f"{col_letter}{i}"
                                            updates.append({
                                                'range': cell_range,
                                                'values': [['terbayar']]
                                            })
                                    
                                    if updates:
                                        worksheet_presensi.batch_update(updates)
                                        st.success(f"✅ Berhasil mengupdate {len(updates)} baris presensi.")
                                        
                                        # Refresh data
                                        refresh_data_in_session()
                                        st.rerun()
                                    else:
                                        st.warning("Tidak ada baris presensi yang cocok dengan kriteria.")
                                except Exception as e:
                                    st.error(f"Terjadi error: {e}")
                
                with col_e3:
                    # Tombol reset filter
                    if st.button("🔄 Reset Filter", key="reset_filter_terbayar"):
                        st.rerun()
            
            else:
                st.info("📭 Tidak ada data sesuai dengan filter yang dipilih")
        
        else:
            st.info("📭 Belum ada data presensi")

import streamlit as st
import pandas as pd
from datetime import time
from utils import (
    get_spreadsheet, refresh_data_in_session, load_data_cached,
    parse_time, get_gspread_client
)

def halaman_monitoring_timebreak():
    st.title("⏰ Monitoring Timebreak Departemen")
    st.markdown("Kelola data departemen dan sub departemen untuk perhitungan UMUT")
    
    # Load data dari session state
    if 'data_departemen' in st.session_state:
        df_dept = st.session_state.data_departemen
    else:
        df_dept = load_data_cached("departemen")
    
    if 'data_subdepartemen' in st.session_state:
        df_sub = st.session_state.data_subdepartemen
    else:
        df_sub = load_data_cached("sub_departemen")
    
    # Tabs
    tab1, tab2 = st.tabs(["🏢 Data Departemen", "👥 Data Sub Departemen"])
    
    # ============================================
    # TAB 1: DATA DEPARTEMEN
    # ============================================
    with tab1:
        st.subheader("🏢 Manajemen Data Departemen")
        st.markdown("Data jam istirahat akan digunakan untuk perhitungan UMUT")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not df_dept.empty:
                # Tampilkan data dengan format yang rapi
                df_display = df_dept.copy()
                df_display.columns = ['ID', 'Nama Departemen', 'Mulai', 'Akhir']
                st.dataframe(df_display, use_container_width=True, height=300)
            else:
                st.info("📭 Belum ada data departemen")
        
        with col2:
            st.metric("Total Departemen", len(df_dept))
        
        st.divider()
        
        # Form Tambah/Edit Departemen
        with st.expander("➕ Tambah Data Departemen Baru", expanded=False):
            with st.form("form_tambah_departemen"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    id_dept = st.number_input(
                        "ID Departemen *",
                        min_value=1,
                        max_value=999,
                        step=1,
                        help="Contoh: 101, 102, 103"
                    )
                    nama_dept = st.text_input(
                        "Nama Departemen *",
                        placeholder="Contoh: IT, HR&GA, PLANT"
                    )
                
                with col_b:
                    mulai = st.time_input(
                        "Mulai Istirahat *",
                        value=time(12, 0),
                        step=60
                    )
                    akhir = st.time_input(
                        "Akhir Istirahat *",
                        value=time(13, 0),
                        step=60
                    )
                
                # Validasi durasi
                if mulai and akhir:
                    durasi = (pd.to_datetime(str(akhir)) - pd.to_datetime(str(mulai))).seconds / 3600
                    if durasi <= 0:
                        st.error("❌ Akhir istirahat harus lebih besar dari mulai istirahat!")
                    else:
                        st.info(f"⏱️ Durasi istirahat: {durasi:.1f} jam")
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    submitted = st.form_submit_button(
                        "💾 SIMPAN DEPARTEMEN",
                        use_container_width=True,
                        type="primary"
                    )
                
                if submitted:
                    if not nama_dept:
                        st.error("❌ Nama departemen harus diisi!")
                    elif mulai >= akhir:
                        st.error("❌ Akhir istirahat harus lebih besar dari mulai istirahat!")
                    else:
                        # Cek duplikat ID
                        if id_dept in df_dept['id_departemen'].values:
                            st.error(f"❌ ID Departemen {id_dept} sudah ada!")
                        else:
                            # Simpan ke Google Sheets
                            with st.spinner("Menyimpan data..."):
                                success, msg = simpan_departemen(
                                    id_dept, nama_dept, 
                                    mulai.strftime("%H:%M"), 
                                    akhir.strftime("%H:%M")
                                )
                                if success:
                                    st.success(f"✅ {msg}")
                                    refresh_data_in_session()
                                    st.rerun()
                                else:
                                    st.error(f"❌ {msg}")
        
        # Edit/Hapus Departemen
        if not df_dept.empty:
            st.divider()
            st.subheader("✏️ Edit / Hapus Departemen")
            
            # Pilih departemen
            dept_options = df_dept.apply(
                lambda row: f"{row['id_departemen']} - {row['nama_departemen']}", 
                axis=1
            ).tolist()
            
            selected = st.selectbox(
                "Pilih Departemen:",
                options=dept_options,
                key="select_dept_edit"
            )
            
            if selected:
                selected_id = int(selected.split(" - ")[0])
                selected_data = df_dept[df_dept['id_departemen'] == selected_id].iloc[0]
                
                col_edit1, col_edit2 = st.columns(2)
                
                with col_edit1:
                    if st.button("✏️ Edit Data", use_container_width=True, type="primary"):
                        st.session_state.edit_dept = selected_data.to_dict()
                        st.rerun()
                
                with col_edit2:
                    if st.button("🗑️ Hapus Data", use_container_width=True):
                        st.session_state.hapus_dept = selected_data.to_dict()
                        st.rerun()
            
            # Form Edit
            if 'edit_dept' in st.session_state:
                st.divider()
                st.markdown("### ✏️ Form Edit Departemen")
                data = st.session_state.edit_dept
                
                with st.form("form_edit_departemen"):
                    col_e1, col_e2 = st.columns(2)
                    
                    with col_e1:
                        edit_id = st.number_input(
                            "ID Departemen",
                            value=int(data['id_departemen']),
                            disabled=True
                        )
                        edit_nama = st.text_input(
                            "Nama Departemen",
                            value=data['nama_departemen']
                        )
                    
                    with col_e2:
                        # Parse waktu dari string
                        try:
                            mulai_default = pd.to_datetime(data['Mulai Istirahat'], format='%H:%M').time()
                        except:
                            mulai_default = time(12, 0)
                        
                        try:
                            akhir_default = pd.to_datetime(data['Akhir Istirahat'], format='%H:%M').time()
                        except:
                            akhir_default = time(13, 0)
                        
                        edit_mulai = st.time_input(
                            "Mulai Istirahat",
                            value=mulai_default
                        )
                        edit_akhir = st.time_input(
                            "Akhir Istirahat",
                            value=akhir_default
                        )
                    
                    col_btn_e1, col_btn_e2, col_btn_e3 = st.columns([1, 1, 2])
                    
                    with col_btn_e1:
                        if st.form_submit_button("💾 Update", use_container_width=True, type="primary"):
                            if not edit_nama:
                                st.error("❌ Nama departemen harus diisi!")
                            elif edit_mulai >= edit_akhir:
                                st.error("❌ Akhir istirahat harus lebih besar dari mulai istirahat!")
                            else:
                                with st.spinner("Mengupdate data..."):
                                    success, msg = update_departemen(
                                        edit_id,
                                        edit_nama,
                                        edit_mulai.strftime("%H:%M"),
                                        edit_akhir.strftime("%H:%M")
                                    )
                                    if success:
                                        st.success(f"✅ {msg}")
                                        del st.session_state.edit_dept
                                        refresh_data_in_session()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                    
                    with col_btn_e2:
                        if st.form_submit_button("❌ Batal", use_container_width=True):
                            del st.session_state.edit_dept
                            st.rerun()
            
            # Konfirmasi Hapus
            if 'hapus_dept' in st.session_state:
                st.divider()
                st.error("⚠️ **KONFIRMASI HAPUS DEPARTEMEN**")
                data_hapus = st.session_state.hapus_dept
                
                st.warning(f"Anda akan menghapus: **{data_hapus['nama_departemen']}** (ID: {data_hapus['id_departemen']})")
                st.warning("⚠️ Data sub departemen yang terkait juga akan dihapus!")
                
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    if st.button("✅ Ya, Hapus", use_container_width=True, type="primary"):
                        with st.spinner("Menghapus data..."):
                            # Hapus departemen
                            success, msg = hapus_departemen(data_hapus['id_departemen'])
                            if success:
                                st.success(f"✅ {msg}")
                                del st.session_state.hapus_dept
                                refresh_data_in_session()
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                
                with col_h2:
                    if st.button("❌ Batal", use_container_width=True):
                        del st.session_state.hapus_dept
                        st.rerun()
    
    # ============================================
    # TAB 2: DATA SUB DEPARTEMEN
    # ============================================
    with tab2:
        st.subheader("👥 Manajemen Data Sub Departemen")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not df_sub.empty and not df_dept.empty:
                # Merge dengan departemen untuk tampilan
                df_sub_display = df_sub.merge(
                    df_dept[['id_departemen', 'nama_departemen']],
                    on='id_departemen',
                    how='left'
                )
                df_sub_display = df_sub_display[['id_subdepartmen', 'nama_subdepartmen', 'nama_departemen']]
                df_sub_display.columns = ['ID Sub', 'Nama Sub Departemen', 'Departemen']
                
                st.dataframe(df_sub_display, use_container_width=True, height=300)
            else:
                if df_dept.empty:
                    st.warning("⚠️ Data departemen kosong. Isi data departemen terlebih dahulu.")
                else:
                    st.info("📭 Belum ada data sub departemen")
        
        with col2:
            st.metric("Total Sub Departemen", len(df_sub))
        
        st.divider()
        
        # Form Tambah Sub Departemen
        if not df_dept.empty:
            with st.expander("➕ Tambah Sub Departemen Baru", expanded=False):
                with st.form("form_tambah_subdepartemen"):
                    # Pilih departemen
                    dept_options = df_dept.apply(
                        lambda row: f"{row['id_departemen']} - {row['nama_departemen']}", 
                        axis=1
                    ).tolist()
                    
                    selected_dept = st.selectbox(
                        "Pilih Departemen *",
                        options=dept_options,
                        key="select_dept_sub"
                    )
                    
                    if selected_dept:
                        id_dept = int(selected_dept.split(" - ")[0])
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        id_sub = st.number_input(
                            "ID Sub Departemen *",
                            min_value=1,
                            max_value=99999,
                            step=1,
                            help="Contoh: 10100, 10101"
                        )
                    
                    with col_b:
                        nama_sub = st.text_input(
                            "Nama Sub Departemen *",
                            placeholder="Contoh: HR, GA, HSE"
                        )
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2:
                        submitted_sub = st.form_submit_button(
                            "💾 SIMPAN SUB DEPARTEMEN",
                            use_container_width=True,
                            type="primary"
                        )
                    
                    if submitted_sub:
                        if not nama_sub:
                            st.error("❌ Nama sub departemen harus diisi!")
                        elif id_sub in df_sub['id_subdepartmen'].values:
                            st.error(f"❌ ID Sub Departemen {id_sub} sudah ada!")
                        else:
                            with st.spinner("Menyimpan data..."):
                                success, msg = simpan_subdepartemen(
                                    id_dept, id_sub, nama_sub
                                )
                                if success:
                                    st.success(f"✅ {msg}")
                                    refresh_data_in_session()
                                    st.rerun()
                                else:
                                    st.error(f"❌ {msg}")
        
        # Edit/Hapus Sub Departemen
        if not df_sub.empty:
            st.divider()
            st.subheader("✏️ Edit / Hapus Sub Departemen")
            
            # Pilih sub departemen
            sub_options = df_sub.apply(
                lambda row: f"{row['id_subdepartmen']} - {row['nama_subdepartmen']}", 
                axis=1
            ).tolist()
            
            selected_sub = st.selectbox(
                "Pilih Sub Departemen:",
                options=sub_options,
                key="select_sub_edit"
            )
            
            if selected_sub:
                selected_id_sub = int(selected_sub.split(" - ")[0])
                selected_sub_data = df_sub[df_sub['id_subdepartmen'] == selected_id_sub].iloc[0]
                
                col_edit1, col_edit2 = st.columns(2)
                
                with col_edit1:
                    if st.button("✏️ Edit Sub Departemen", use_container_width=True, type="primary"):
                        st.session_state.edit_sub = selected_sub_data.to_dict()
                        st.rerun()
                
                with col_edit2:
                    if st.button("🗑️ Hapus Sub Departemen", use_container_width=True):
                        st.session_state.hapus_sub = selected_sub_data.to_dict()
                        st.rerun()
            
            # Form Edit Sub
            if 'edit_sub' in st.session_state:
                st.divider()
                st.markdown("### ✏️ Form Edit Sub Departemen")
                data_sub = st.session_state.edit_sub
                
                with st.form("form_edit_subdepartemen"):
                    dept_options = df_dept.apply(
                        lambda row: f"{row['id_departemen']} - {row['nama_departemen']}", 
                        axis=1
                    ).tolist()
                    
                    current_dept = f"{data_sub['id_departemen']} - {df_dept[df_dept['id_departemen'] == data_sub['id_departemen']]['nama_departemen'].values[0]}"
                    
                    selected_dept_edit = st.selectbox(
                        "Pilih Departemen",
                        options=dept_options,
                        index=dept_options.index(current_dept) if current_dept in dept_options else 0
                    )
                    
                    id_dept_edit = int(selected_dept_edit.split(" - ")[0])
                    
                    col_e1, col_e2 = st.columns(2)
                    
                    with col_e1:
                        edit_id_sub = st.number_input(
                            "ID Sub Departemen",
                            value=int(data_sub['id_subdepartmen']),
                            disabled=True
                        )
                    
                    with col_e2:
                        edit_nama_sub = st.text_input(
                            "Nama Sub Departemen",
                            value=data_sub['nama_subdepartmen']
                        )
                    
                    col_btn_e1, col_btn_e2, col_btn_e3 = st.columns([1, 1, 2])
                    
                    with col_btn_e1:
                        if st.form_submit_button("💾 Update", use_container_width=True, type="primary"):
                            if not edit_nama_sub:
                                st.error("❌ Nama sub departemen harus diisi!")
                            else:
                                with st.spinner("Mengupdate data..."):
                                    success, msg = update_subdepartemen(
                                        edit_id_sub,
                                        id_dept_edit,
                                        edit_nama_sub
                                    )
                                    if success:
                                        st.success(f"✅ {msg}")
                                        del st.session_state.edit_sub
                                        refresh_data_in_session()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                    
                    with col_btn_e2:
                        if st.form_submit_button("❌ Batal", use_container_width=True):
                            del st.session_state.edit_sub
                            st.rerun()
            
            # Konfirmasi Hapus Sub
            if 'hapus_sub' in st.session_state:
                st.divider()
                st.error("⚠️ **KONFIRMASI HAPUS SUB DEPARTEMEN**")
                data_hapus_sub = st.session_state.hapus_sub
                
                st.warning(f"Anda akan menghapus: **{data_hapus_sub['nama_subdepartmen']}** (ID: {data_hapus_sub['id_subdepartmen']})")
                
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    if st.button("✅ Ya, Hapus", use_container_width=True, type="primary"):
                        with st.spinner("Menghapus data..."):
                            success, msg = hapus_subdepartemen(data_hapus_sub['id_subdepartmen'])
                            if success:
                                st.success(f"✅ {msg}")
                                del st.session_state.hapus_sub
                                refresh_data_in_session()
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                
                with col_h2:
                    if st.button("❌ Batal", use_container_width=True):
                        del st.session_state.hapus_sub
                        st.rerun()


# ============================================
# FUNGSI CRUD UNTUK DEPARTEMEN
# ============================================
def simpan_departemen(id_dept, nama_dept, mulai, akhir):
    """Menyimpan data departemen baru"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
        
        worksheet = spreadsheet.worksheet("departemen")
        
        # Siapkan data baru
        new_row = [str(id_dept), nama_dept, mulai, akhir]
        
        # Tambahkan di baris ke-2
        worksheet.insert_row(new_row, index=2)
        
        return True, f"Departemen {nama_dept} berhasil disimpan"
        
    except Exception as e:
        return False, str(e)

def update_departemen(id_dept, nama_dept, mulai, akhir):
    """Mengupdate data departemen"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
        
        worksheet = spreadsheet.worksheet("departemen")
        
        # Ambil semua data
        all_data = worksheet.get_all_values()
        
        # Cari baris dengan ID yang sesuai
        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 0 and str(row[0]) == str(id_dept):
                # Update baris
                update_range = f'A{i}:D{i}'
                worksheet.update(update_range, [[str(id_dept), nama_dept, mulai, akhir]])
                return True, f"Departemen {nama_dept} berhasil diupdate"
        
        return False, f"ID Departemen {id_dept} tidak ditemukan"
        
    except Exception as e:
        return False, str(e)

def hapus_departemen(id_dept):
    """Menghapus data departemen dan sub departemen terkait"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
        
        # Hapus sub departemen terkait dulu
        worksheet_sub = spreadsheet.worksheet("sub_departemen")
        all_sub = worksheet_sub.get_all_values()
        
        baris_sub_hapus = []
        for i, row in enumerate(all_sub[1:], start=2):
            if len(row) > 0 and str(row[0]) == str(id_dept):
                baris_sub_hapus.append(i)
        
        for baris in sorted(baris_sub_hapus, reverse=True):
            worksheet_sub.delete_rows(baris)
        
        # Hapus departemen
        worksheet_dept = spreadsheet.worksheet("departemen")
        all_dept = worksheet_dept.get_all_values()
        
        for i, row in enumerate(all_dept[1:], start=2):
            if len(row) > 0 and str(row[0]) == str(id_dept):
                worksheet_dept.delete_rows(i)
                return True, f"Departemen dan {len(baris_sub_hapus)} sub departemen berhasil dihapus"
        
        return False, f"ID Departemen {id_dept} tidak ditemukan"
        
    except Exception as e:
        return False, str(e)


# ============================================
# FUNGSI CRUD UNTUK SUB DEPARTEMEN
# ============================================
def simpan_subdepartemen(id_dept, id_sub, nama_sub):
    """Menyimpan data sub departemen baru"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
        
        worksheet = spreadsheet.worksheet("sub_departemen")
        
        # Siapkan data baru
        new_row = [str(id_dept), str(id_sub), nama_sub]
        
        # Tambahkan di baris ke-2
        worksheet.insert_row(new_row, index=2)
        
        return True, f"Sub departemen {nama_sub} berhasil disimpan"
        
    except Exception as e:
        return False, str(e)

def update_subdepartemen(id_sub, id_dept, nama_sub):
    """Mengupdate data sub departemen"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
        
        worksheet = spreadsheet.worksheet("sub_departemen")
        
        # Ambil semua data
        all_data = worksheet.get_all_values()
        
        # Cari baris dengan ID sub yang sesuai
        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 1 and str(row[1]) == str(id_sub):
                # Update baris
                update_range = f'A{i}:C{i}'
                worksheet.update(update_range, [[str(id_dept), str(id_sub), nama_sub]])
                return True, f"Sub departemen {nama_sub} berhasil diupdate"
        
        return False, f"ID Sub Departemen {id_sub} tidak ditemukan"
        
    except Exception as e:
        return False, str(e)

def hapus_subdepartemen(id_sub):
    """Menghapus data sub departemen"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
        
        worksheet = spreadsheet.worksheet("sub_departemen")
        
        # Ambil semua data
        all_data = worksheet.get_all_values()
        
        # Cari baris dengan ID sub yang sesuai
        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 1 and str(row[1]) == str(id_sub):
                worksheet.delete_rows(i)
                return True, f"Sub departemen berhasil dihapus"
        
        return False, f"ID Sub Departemen {id_sub} tidak ditemukan"
        
    except Exception as e:
        return False, str(e)
    

# =========================
# MAIN APP
# =========================
def main():
    # Load CSS
    load_css()
    
    # Inisialisasi session state
    init_session_state()
    
    # Cek status login
    if not st.session_state.logged_in:
        halaman_login()
        return
    
    show_sidebar()


    if st.session_state.current_page == 'pendaftaran':
        halaman_entry_data()
    elif st.session_state.current_page == 'Magang Analytic':
        halaman_Magang_Analytic()
    elif st.session_state.current_page == 'Update Presensi':
        halaman_Update_Presensi()
    elif st.session_state.current_page == 'Rekapitulasi Kehadiran':
        halaman_Rekapitulasi_Presensi()
    elif st.session_state.current_page == 'monitoring_timebreak':  # <-- TAMBAHKAN INI
        halaman_monitoring_timebreak()
    else:
        halaman_entry_data()

if __name__ == "__main__":
    main()
