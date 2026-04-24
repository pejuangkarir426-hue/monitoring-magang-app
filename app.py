import streamlit as st
from config import APP_CONFIG

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN (harus paling atas)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title=APP_CONFIG['nama_aplikasi'],
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# IMPORT MODUL
# ─────────────────────────────────────────────
from styles import load_css
from components.sidebar import show_sidebar
from halaman.login import halaman_login
from halaman.entry_data import halaman_entry_data
from halaman.analytic import halaman_Magang_Analytic
from halaman.presensi import halaman_Update_Presensi
from halaman.rekapitulasi import halaman_Rekapitulasi_Presensi
from halaman.monitoring_timebreak import halaman_monitoring_timebreak
# from halaman.approved import halaman_approved_magang
# from halaman.monitoring_kapasitas import halaman_monitoring_kapasitas
# from halaman.master_data import halaman_master_data


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# ROUTER HALAMAN
# ─────────────────────────────────────────────
PAGE_MAP = {
    'pendaftaran': halaman_entry_data,
    'Magang Analytic': halaman_Magang_Analytic,
    'Update Presensi': halaman_Update_Presensi,
    'Rekapitulasi Kehadiran': halaman_Rekapitulasi_Presensi,
    'monitoring_timebreak': halaman_monitoring_timebreak
    # 'approved_magang': halaman_approved_magang,
    # 'monitoring_kapasitas': halaman_monitoring_kapasitas,
    # 'master_data': halaman_master_data
}


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    load_css()
    init_session_state()

    if not st.session_state.logged_in:
        halaman_login()
        return

    show_sidebar()

    page_fn = PAGE_MAP.get(st.session_state.current_page, halaman_entry_data)
    page_fn()


if __name__ == "__main__":
    main()
