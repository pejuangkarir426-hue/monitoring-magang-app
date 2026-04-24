import streamlit as st
import time as tm
from utils import authenticate_user1, load_data_cached


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
