import streamlit as st
import pandas as pd
from datetime import datetime
import time as tm
from dateutil.relativedelta import relativedelta
from utils import (
    save_internship_data, refresh_data_in_session,
    delete_internship_data, update_internship_data
)
from config import jenissekolah_list, periode_list


def halaman_entry_data():
    st.markdown("""
    <div class="premium-header">
        <h1><i class="fas fa-user-graduate"></i> Program Magang JAPFA</h1>
        <p>PT Japfa Comfeed Indonesia Tbk - Sidoarjo</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tab style
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border: 2px solid #D1D5DB;
        border-radius: 12px;
        padding: 10px 22px;
        font-weight: 600;
        color: #374151;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { border: 2px solid #FC5000; color: #FC5000; }
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
        _tab_input_data()

    with tab2:
        _tab_edit_data()


def _tab_input_data():
    df_dept = st.session_state.data_departemen
    df_subdept = st.session_state.data_subdepartemen
    departemen_list = df_dept["nama_departemen"].tolist()

    # DATA PRIBADI
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
            id_dept = df_dept[df_dept["nama_departemen"] == dept]["id_departemen"].values[0]
            subdept_options = df_subdept[df_subdept["id_departemen"] == id_dept]["nama_subdepartmen"].tolist()
            subdept = st.selectbox("Sub Departemen *", subdept_options)
            keterangan = st.text_input("Keterangan *", placeholder="Keterangan tambahan")

    st.divider()

    # JADWAL MAGANG
    with st.container():
        st.subheader("Jadwal Magang")
        col3, col4 = st.columns(2)
        now = datetime.now().date()

        with col3:
            tgl_mulai = st.date_input("Tanggal Mulai *", value=now)
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

    # PREVIEW & SUBMIT
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

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("DAFTAR SEKARANG", use_container_width=True, type="primary"):
            if not all([id_magang, nama, jurusan, sekolah]):
                st.error("❌ Semua field wajib harus diisi!")
            else:
                bulan_indo = [
                    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
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
                if save_internship_data(form_data):
                    st.success("✅ Pendaftaran berhasil!")
                    st.balloons()
                    tm.sleep(2)
                    st.rerun()


def _tab_edit_data():
    st.title("✏️ Edit & Hapus Data Magang")

    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = False
    if 'selected_data' not in st.session_state:
        st.session_state.selected_data = None
    if 'data_to_delete' not in st.session_state:
        st.session_state.data_to_delete = None

    df_magang = st.session_state.data_magang
    df_dept = st.session_state.data_departemen
    df_subdept = st.session_state.data_subdepartemen

    if len(df_magang) > 0:
        with st.container():
            st.subheader("🔍 Pencarian Data")
            col_search1, col_search2, col_search3 = st.columns([2, 2, 1])

            with col_search1:
                search_id = st.text_input("Cari ID Magang", placeholder="Masukkan ID Magang...", key="search_id_edit")
            with col_search2:
                search_nama = st.text_input("Cari Nama", placeholder="Masukkan Nama...", key="search_nama_edit")
            with col_search3:
                st.button("🔎 Cari", use_container_width=True, key="search_btn_edit")

            filtered_df = df_magang.copy()
            if search_id:
                filtered_df = filtered_df[filtered_df['ID_Magang'].astype(str).str.contains(search_id, case=False, na=False)]
            if search_nama:
                filtered_df = filtered_df[filtered_df['Nama'].astype(str).str.contains(search_nama, case=False, na=False)]
            if search_id or search_nama:
                st.write(f"Ditemukan **{len(filtered_df)}** data")

        st.divider()

        if len(filtered_df) > 0:
            selected_id = st.selectbox(
                "📋 Pilih Data:",
                options=filtered_df['ID_Magang'].tolist(),
                format_func=lambda x: f"{x} - {filtered_df[filtered_df['ID_Magang']==x]['Nama'].values[0]}",
                key="select_id_edit"
            )

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

            col_action1, col_action2, col_action3 = st.columns([1, 1, 2])

            with col_action1:
                if st.button("✏️ UBAH DATA", use_container_width=True, type="primary", key="btn_edit_data"):
                    st.session_state.selected_data = filtered_df[filtered_df['ID_Magang'] == selected_id].iloc[0].to_dict()
                    st.session_state.edit_mode = True
                    st.session_state.delete_confirmation = False
                    st.rerun()

            with col_action2:
                if st.button("🗑️ HAPUS DATA", use_container_width=True, type="secondary", key="btn_delete_data"):
                    st.session_state.data_to_delete = filtered_df[filtered_df['ID_Magang'] == selected_id].iloc[0].to_dict()
                    st.session_state.delete_confirmation = True
                    st.session_state.edit_mode = False
                    st.rerun()

            st.divider()

            # Konfirmasi Hapus
            if st.session_state.delete_confirmation and st.session_state.data_to_delete:
                data_hapus = st.session_state.data_to_delete

                with st.container(border=True):
                    st.error("⚠️ **KONFIRMASI HAPUS DATA**")
                    st.warning("Anda akan menghapus data berikut:")

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
                                    success = delete_internship_data(data_hapus['ID_Magang'])
                                    if success:
                                        st.session_state.delete_confirmation = False
                                        st.session_state.data_to_delete = None
                                        st.success(f"✅ Data {data_hapus['ID_Magang']} - {data_hapus['Nama']} berhasil dihapus!")
                                        refresh_data_in_session()
                                        tm.sleep(2)
                                        st.rerun()
                                    else:
                                        st.error("❌ Gagal menghapus data!")
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
        else:
            if search_id or search_nama:
                st.warning("⚠️ Tidak ada data yang sesuai dengan pencarian")
            with st.expander("📊 Lihat Semua Data", expanded=False):
                st.dataframe(df_magang, use_container_width=True)
    else:
        st.info("📭 Belum ada data magang")

    # Form Edit Data
    if st.session_state.edit_mode and st.session_state.selected_data:
        selected_data = st.session_state.selected_data

        st.subheader("✏️ Form Edit Data")
        st.info(f"Mengedit data: **{selected_data['ID_Magang']} - {selected_data['Nama']}**")

        if st.button("❌ Batal Edit", key="cancel_edit_btn"):
            st.session_state.edit_mode = False
            st.session_state.selected_data = None
            st.rerun()

        st.divider()

        with st.container():
            st.markdown("##### 📋 Data Pribadi")
            col1, col2 = st.columns(2)

            with col1:
                edit_id_magang = st.text_input("ID Magang *", value=selected_data['ID_Magang'], disabled=True, help="ID Magang tidak dapat diubah", key="edit_id_magang")
                edit_nama = st.text_input("Nama *", value=selected_data['Nama'], placeholder="Sesuai KTP", key="edit_nama")
                jk_index = 0 if selected_data['Jenis Kelamin'] == "Laki-laki" else 1
                edit_jenis_kelamin = st.selectbox("Jenis Kelamin *", ["Laki-laki", "Perempuan"], index=jk_index, key="edit_jenis_kelamin")
                edit_jurusan = st.text_input("Jurusan *", value=selected_data['Jurusan/Fakultas'], placeholder="Contoh: Teknik Informatika", key="edit_jurusan")
                jenjang_options = ["SMA/SMK", "D3", "D4", "S1", "S2"]
                try:
                    jenjang_index = jenjang_options.index(selected_data['Jenjang']) if selected_data['Jenjang'] in jenjang_options else 0
                except:
                    jenjang_index = 0
                edit_jenjang = st.selectbox("Jenjang *", jenjang_options, index=jenjang_index, key="edit_jenjang")

            with col2:
                edit_sekolah = st.text_input("Sekolah/Universitas *", value=selected_data['Sekolah/Universitas'], placeholder="Nama institusi", key="edit_sekolah")
                jenis_sekolah_options = ["Universitas", "Sekolah"]
                try:
                    jenis_index = jenis_sekolah_options.index(selected_data['Jenis Univ/Sekolah']) if selected_data['Jenis Univ/Sekolah'] in jenis_sekolah_options else 0
                except:
                    jenis_index = 0
                edit_jenis_univ_sekolah = st.selectbox("Jenis Sekolah/Univ *", jenis_sekolah_options, index=jenis_index, key="edit_jenis_univ")

                departemen_list = df_dept["nama_departemen"].tolist()
                try:
                    dept_index = departemen_list.index(selected_data['Bagian/Dept']) if selected_data['Bagian/Dept'] in departemen_list else 0
                except:
                    dept_index = 0
                edit_dept = st.selectbox("Departemen *", departemen_list, index=dept_index, key="edit_dept")

                id_dept = df_dept[df_dept["nama_departemen"] == edit_dept]["id_departemen"].values[0]
                subdept_options = df_subdept[df_subdept["id_departemen"] == id_dept]["nama_subdepartmen"].tolist()
                try:
                    subdept_index = subdept_options.index(selected_data['Sub Dept']) if selected_data['Sub Dept'] in subdept_options else 0
                except:
                    subdept_index = 0
                edit_subdept = st.selectbox("Sub Departemen *", subdept_options, index=subdept_index, key="edit_subdept")
                edit_keterangan = st.text_input("Keterangan", value=selected_data.get('Keterangan', ''), placeholder="Keterangan tambahan (opsional)", key="edit_keterangan")

        st.divider()

        with st.container():
            st.markdown("##### 📅 Jadwal Magang")
            bulan_indo = {
                'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 'Mei': 5, 'Juni': 6,
                'Juli': 7, 'Agustus': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
            }

            try:
                parts = str(selected_data['Mulai']).split()
                tgl_mulai_default = datetime(int(parts[2]), bulan_indo[parts[1]], int(parts[0])).date() if len(parts) == 3 else datetime.now().date()
            except:
                tgl_mulai_default = datetime.now().date()

            try:
                parts = str(selected_data['Akhir']).split()
                tgl_akhir_default = datetime(int(parts[2]), bulan_indo[parts[1]], int(parts[0])).date() if len(parts) == 3 else datetime.now().date()
            except:
                tgl_akhir_default = datetime.now().date()

            col3, col4 = st.columns(2)
            with col3:
                edit_tgl_mulai = st.date_input("Tanggal Mulai *", value=tgl_mulai_default, key="edit_tgl_mulai")
                durasi_options = [3, 4, 5, 6]
                try:
                    durasi_index = durasi_options.index(int(selected_data['Bulan'])) if int(selected_data['Bulan']) in durasi_options else 0
                except:
                    durasi_index = 0
                edit_durasi = st.selectbox("Durasi (bulan) *", durasi_options, index=durasi_index, key="edit_durasi")
                tgl_akhir_otomatis = edit_tgl_mulai + relativedelta(months=edit_durasi)
                st.info(f"Rekomendasi : **{tgl_akhir_otomatis.strftime('%d/%m/%Y')}**")

            with col4:
                edit_tgl_akhir = st.date_input("Tanggal Akhir", value=tgl_akhir_default, min_value=edit_tgl_mulai, key="edit_tgl_akhir")
                periode_options = ["Semester I", "Semester II"]
                try:
                    periode_index = periode_options.index(selected_data['Periode']) if selected_data['Periode'] in periode_options else 0
                except:
                    periode_index = 0
                edit_periode = st.selectbox("Periode *", periode_options, index=periode_index, key="edit_periode")
                st.text_input("Tahun", value=str(edit_tgl_mulai.year), disabled=True, key="edit_tahun")

        st.divider()

        bulan_indo_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

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
            tgl_mulai_format = f"{edit_tgl_mulai.day} {bulan_indo_list[edit_tgl_mulai.month-1]} {edit_tgl_mulai.year}"
            tgl_akhir_format = f"{edit_tgl_akhir.day} {bulan_indo_list[edit_tgl_akhir.month-1]} {edit_tgl_akhir.year}"
            st.write(f"**Jadwal:** {tgl_mulai_format} - {tgl_akhir_format} ({edit_durasi} bulan)")

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("💾 UPDATE DATA", use_container_width=True, type="primary", key="btn_update"):
                if not all([edit_nama, edit_jurusan, edit_sekolah]):
                    st.error("❌ Semua field wajib harus diisi!")
                else:
                    tgl_mulai_format = f"{edit_tgl_mulai.day} {bulan_indo_list[edit_tgl_mulai.month-1]} {edit_tgl_mulai.year}"
                    tgl_akhir_format = f"{edit_tgl_akhir.day} {bulan_indo_list[edit_tgl_akhir.month-1]} {edit_tgl_akhir.year}"
                    updated_data = {
                        'ID_Magang': edit_id_magang, 'Nama': edit_nama,
                        'Jenis Kelamin': edit_jenis_kelamin, 'Jurusan/Fakultas': edit_jurusan,
                        'Jenjang': edit_jenjang, 'Sekolah/Universitas': edit_sekolah,
                        'Jenis Univ/Sekolah': edit_jenis_univ_sekolah, 'Bagian/Dept': edit_dept,
                        'Sub Dept': edit_subdept, 'Bulan': edit_durasi,
                        'Mulai': tgl_mulai_format, 'Akhir': tgl_akhir_format,
                        'Periode': edit_periode, 'Tahun': edit_tgl_mulai.year,
                        'Keterangan': edit_keterangan, 'Catatan': selected_data.get('Catatan', '')
                    }
                    with st.spinner("Mengupdate data..."):
                        if update_internship_data(edit_id_magang, updated_data):
                            st.session_state.edit_mode = False
                            st.session_state.selected_data = None
                            st.success("✅ Data berhasil diupdate!")
                            st.balloons()
                            refresh_data_in_session()
                            tm.sleep(2)
                            st.rerun()
