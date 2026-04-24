import streamlit as st
import time as tm
from utils import load_data_cached, refresh_data_in_session


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


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
        background-color: #f5f5f5;
    }

    /* Active */
    div[role="radiogroup"] label:has(input:checked) {
        background-color: #FC5000;
        color: white !important;
    }

    /* Style group header */
    .menu-group-header {
        padding: 10px 20px 4px 20px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #999 !important;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-top: 8px;
    }

    /* Style group button (collapsed/expanded) */
    .group-btn {
        width: 100%;
        padding: 14px 20px;
        background: none;
        border: none;
        text-align: left;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        color: #333 !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background 0.2s;
    }
    .group-btn:hover {
        background-color: #f5f5f5;
    }
    .group-btn.active-group {
        color: #FC5000 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Logo
        st.image("assets/Logo japfa tanpa BG.png", width=100)

        st.markdown("""
        <hr style="border:1.5px solid #2D7DAF; margin:6px 0;">
        """, unsafe_allow_html=True)

        # ── Inisialisasi active group di session state ──
        if 'active_group' not in st.session_state:
            st.session_state.active_group = 'magang'  # default buka grup magang

        # ══════════════════════════════════════
        # GRUP 1 — MANAJEMEN MAGANG
        # ══════════════════════════════════════
        col_g2, col_arr2 = st.columns([5, 1])
        with col_g2:
            st.markdown("**🎓 Manajemen Magang**")
        with col_arr2:
            arrow2 = "▲" if st.session_state.active_group == 'magang' else "▼"
            if st.button(arrow2, key="toggle_magang", use_container_width=True):
                if st.session_state.active_group == 'magang':
                    st.session_state.active_group = None
                else:
                    st.session_state.active_group = 'magang'
                st.rerun()

        if st.session_state.active_group == 'magang':
            st.markdown('<div class="menu-group-header">Menu</div>', unsafe_allow_html=True)
            menu_magang = st.radio(
                " ",
                [
                    "  Entry Data",
                    "  Magang Analytic",
                    "  Update Presensi",
                    "  Rekapitulasi Kehadiran",
                    "  Monitoring Timebreak",
                ],
                key="radio_magang"
            )

            # Mapping halaman
            menu_map = {
                "  Entry Data": "pendaftaran",
                "  Magang Analytic": "Magang Analytic",
                "  Update Presensi": "Update Presensi",
                "  Rekapitulasi Kehadiran": "Rekapitulasi Kehadiran",
                "  Monitoring Timebreak": "monitoring_timebreak",
            }

            selected_page = menu_map[menu_magang]

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
                    st.cache_data.clear()
                    st.session_state.data_magang = load_data_cached("database_magang")
                    st.session_state.data_presensi = load_data_cached("data_presensi")
                    st.session_state.data_departemen = load_data_cached("departemen")
                    st.session_state.data_subdepartemen = load_data_cached("sub_departemen")
                st.success("✅ Data berhasil diperbarui!")
                tm.sleep(1)
                st.rerun()

        with col2:
            if st.button("Keluar", use_container_width=True):
                logout()

        # Tampilkan info kapan terakhir di-refresh
        from datetime import datetime
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")
        st.caption(f"Terakhir update: {st.session_state.last_refresh}")