import streamlit as st
import pandas as pd
from datetime import time
from utils import (
    get_spreadsheet, refresh_data_in_session, load_data_cached
)


# ============================================
# FUNGSI CRUD DEPARTEMEN
# ============================================

def simpan_departemen(id_dept, nama_dept, mulai, akhir):
    """Menyimpan data departemen baru"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
        worksheet = spreadsheet.worksheet("departemen")
        worksheet.insert_row([str(id_dept), nama_dept, mulai, akhir], index=2)
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
        all_data = worksheet.get_all_values()
        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 0 and str(row[0]) == str(id_dept):
                worksheet.update([[str(id_dept), nama_dept, mulai, akhir]], f'A{i}:D{i}')
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

        worksheet_sub = spreadsheet.worksheet("sub_departemen")
        all_sub = worksheet_sub.get_all_values()
        baris_sub_hapus = [i for i, row in enumerate(all_sub[1:], start=2)
                           if len(row) > 0 and str(row[0]) == str(id_dept)]
        for baris in sorted(baris_sub_hapus, reverse=True):
            worksheet_sub.delete_rows(baris)

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
# FUNGSI CRUD SUB DEPARTEMEN
# ============================================

def simpan_subdepartemen(id_dept, id_sub, nama_sub):
    """Menyimpan data sub departemen baru"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False, "Gagal terhubung ke database"
        worksheet = spreadsheet.worksheet("sub_departemen")
        worksheet.insert_row([str(id_dept), str(id_sub), nama_sub], index=2)
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
        all_data = worksheet.get_all_values()
        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 1 and str(row[1]) == str(id_sub):
                worksheet.update([[str(id_dept), str(id_sub), nama_sub]], f'A{i}:C{i}')
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
        all_data = worksheet.get_all_values()
        for i, row in enumerate(all_data[1:], start=2):
            if len(row) > 1 and str(row[1]) == str(id_sub):
                worksheet.delete_rows(i)
                return True, "Sub departemen berhasil dihapus"
        return False, f"ID Sub Departemen {id_sub} tidak ditemukan"
    except Exception as e:
        return False, str(e)


# ============================================
# HALAMAN UTAMA
# ============================================

def halaman_monitoring_timebreak():
    st.title("⏰ Monitoring Timebreak Departemen")
    st.markdown("Kelola data departemen dan sub departemen untuk perhitungan UMUT")
    st.markdown("**Catatan:** Data jam istirahat akan digunakan untuk menghitung UMUT (Unit Magang dan Unit Timebreak) pada laporan kehadiran magang. Pastikan data departemen dan sub departemen selalu terupdate untuk perhitungan yang akurat.")

    df_dept = st.session_state.get('data_departemen', load_data_cached("departemen"))
    df_sub = st.session_state.get('data_subdepartemen', load_data_cached("sub_departemen"))

    tab1, tab2 = st.tabs(["🏢 Data Departemen", "👥 Data Sub Departemen"])

    # ─────────────────────────────────────────────
    # TAB 1: DEPARTEMEN
    # ─────────────────────────────────────────────
    with tab1:
        st.subheader("🏢 Manajemen Data Departemen")
        st.markdown("Data jam istirahat akan digunakan untuk perhitungan UMUT")

        col1, col2 = st.columns([2, 1])
        with col1:
            if not df_dept.empty:
                df_display = df_dept.copy()
                df_display = df_display[[col for col in df_display.columns
                                         if str(col).strip() != '' and not str(col).strip().isdigit()]]
                df_display.columns = ['ID', 'Nama Departemen', 'Mulai', 'Akhir']
                st.dataframe(df_display, use_container_width=True, height=300)
            else:
                st.info("📭 Belum ada data departemen")
        with col2:
            st.metric("Total Departemen", len(df_dept))

        st.divider()

        with st.expander("➕ Tambah Data Departemen Baru", expanded=False):
            with st.form("form_tambah_departemen"):
                col_a, col_b = st.columns(2)
                with col_a:
                    id_dept = st.number_input("ID Departemen *", min_value=1, max_value=999, step=1, help="Contoh: 101, 102, 103")
                    nama_dept = st.text_input("Nama Departemen *", placeholder="Contoh: IT, HR&GA, PLANT")
                with col_b:
                    mulai = st.time_input("Mulai Istirahat *", value=time(12, 0), step=60)
                    akhir = st.time_input("Akhir Istirahat *", value=time(13, 0), step=60)

                if mulai and akhir:
                    durasi = (pd.to_datetime(str(akhir)) - pd.to_datetime(str(mulai))).seconds / 3600
                    if durasi <= 0:
                        st.error("❌ Akhir istirahat harus lebih besar dari mulai istirahat!")
                    else:
                        st.info(f"⏱️ Durasi istirahat: {durasi:.1f} jam")

                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    submitted = st.form_submit_button("💾 SIMPAN DEPARTEMEN", use_container_width=True, type="primary")

                if submitted:
                    if not nama_dept:
                        st.error("❌ Nama departemen harus diisi!")
                    elif mulai >= akhir:
                        st.error("❌ Akhir istirahat harus lebih besar dari mulai istirahat!")
                    elif id_dept in df_dept['id_departemen'].values:
                        st.error(f"❌ ID Departemen {id_dept} sudah ada!")
                    else:
                        with st.spinner("Menyimpan data..."):
                            success, msg = simpan_departemen(id_dept, nama_dept,
                                                             mulai.strftime("%H:%M"), akhir.strftime("%H:%M"))
                            if success:
                                st.success(f"✅ {msg}")
                                refresh_data_in_session()
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")

        if not df_dept.empty:
            st.divider()
            st.subheader("✏️ Edit / Hapus Departemen")

            dept_options = df_dept.apply(lambda row: f"{row['id_departemen']} - {row['nama_departemen']}", axis=1).tolist()
            selected = st.selectbox("Pilih Departemen:", options=dept_options, key="select_dept_edit")

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

            if 'edit_dept' in st.session_state:
                st.divider()
                st.markdown("### ✏️ Form Edit Departemen")
                data = st.session_state.edit_dept
                with st.form("form_edit_departemen"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        edit_id = st.number_input("ID Departemen", value=int(data['id_departemen']), disabled=True)
                        edit_nama = st.text_input("Nama Departemen", value=data['nama_departemen'])
                    with col_e2:
                        try:
                            mulai_default = pd.to_datetime(data['Mulai Istirahat'], format='%H:%M').time()
                        except:
                            mulai_default = time(12, 0)
                        try:
                            akhir_default = pd.to_datetime(data['Akhir Istirahat'], format='%H:%M').time()
                        except:
                            akhir_default = time(13, 0)
                        edit_mulai = st.time_input("Mulai Istirahat", value=mulai_default)
                        edit_akhir = st.time_input("Akhir Istirahat", value=akhir_default)

                    col_btn_e1, col_btn_e2, col_btn_e3 = st.columns([1, 1, 2])
                    with col_btn_e1:
                        if st.form_submit_button("💾 Update", use_container_width=True, type="primary"):
                            if not edit_nama:
                                st.error("❌ Nama departemen harus diisi!")
                            elif edit_mulai >= edit_akhir:
                                st.error("❌ Akhir istirahat harus lebih besar dari mulai istirahat!")
                            else:
                                with st.spinner("Mengupdate data..."):
                                    success, msg = update_departemen(edit_id, edit_nama,
                                                                     edit_mulai.strftime("%H:%M"),
                                                                     edit_akhir.strftime("%H:%M"))
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

    # ─────────────────────────────────────────────
    # TAB 2: SUB DEPARTEMEN
    # ─────────────────────────────────────────────
    with tab2:
        st.subheader("👥 Manajemen Data Sub Departemen")

        col1, col2 = st.columns([2, 1])
        with col1:
            if not df_sub.empty and not df_dept.empty:
                df_sub_display = df_sub.merge(df_dept[['id_departemen', 'nama_departemen']],
                                              on='id_departemen', how='left')
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

        if not df_dept.empty:
            with st.expander("➕ Tambah Sub Departemen Baru", expanded=False):
                with st.form("form_tambah_subdepartemen"):
                    dept_options = df_dept.apply(lambda row: f"{row['id_departemen']} - {row['nama_departemen']}", axis=1).tolist()
                    selected_dept = st.selectbox("Pilih Departemen *", options=dept_options, key="select_dept_sub")
                    id_dept = int(selected_dept.split(" - ")[0]) if selected_dept else None

                    col_a, col_b = st.columns(2)
                    with col_a:
                        id_sub = st.number_input("ID Sub Departemen *", min_value=1, max_value=99999, step=1, help="Contoh: 10100, 10101")
                    with col_b:
                        nama_sub = st.text_input("Nama Sub Departemen *", placeholder="Contoh: HR, GA, HSE")

                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2:
                        submitted_sub = st.form_submit_button("💾 SIMPAN SUB DEPARTEMEN", use_container_width=True, type="primary")

                    if submitted_sub:
                        if not nama_sub:
                            st.error("❌ Nama sub departemen harus diisi!")
                        elif id_sub in df_sub['id_subdepartmen'].values:
                            st.error(f"❌ ID Sub Departemen {id_sub} sudah ada!")
                        else:
                            with st.spinner("Menyimpan data..."):
                                success, msg = simpan_subdepartemen(id_dept, id_sub, nama_sub)
                                if success:
                                    st.success(f"✅ {msg}")
                                    refresh_data_in_session()
                                    st.rerun()
                                else:
                                    st.error(f"❌ {msg}")

        if not df_sub.empty:
            st.divider()
            st.subheader("✏️ Edit / Hapus Sub Departemen")

            sub_options = df_sub.apply(lambda row: f"{row['id_subdepartmen']} - {row['nama_subdepartmen']}", axis=1).tolist()
            selected_sub = st.selectbox("Pilih Sub Departemen:", options=sub_options, key="select_sub_edit")

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

            if 'edit_sub' in st.session_state:
                st.divider()
                st.markdown("### ✏️ Form Edit Sub Departemen")
                data_sub = st.session_state.edit_sub
                with st.form("form_edit_subdepartemen"):
                    dept_options = df_dept.apply(lambda row: f"{row['id_departemen']} - {row['nama_departemen']}", axis=1).tolist()
                    current_dept = f"{data_sub['id_departemen']} - {df_dept[df_dept['id_departemen'] == data_sub['id_departemen']]['nama_departemen'].values[0]}"
                    selected_dept_edit = st.selectbox(
                        "Pilih Departemen", options=dept_options,
                        index=dept_options.index(current_dept) if current_dept in dept_options else 0)
                    id_dept_edit = int(selected_dept_edit.split(" - ")[0])

                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        edit_id_sub = st.number_input("ID Sub Departemen", value=int(data_sub['id_subdepartmen']), disabled=True)
                    with col_e2:
                        edit_nama_sub = st.text_input("Nama Sub Departemen", value=data_sub['nama_subdepartmen'])

                    col_btn_e1, col_btn_e2, col_btn_e3 = st.columns([1, 1, 2])
                    with col_btn_e1:
                        if st.form_submit_button("💾 Update", use_container_width=True, type="primary"):
                            if not edit_nama_sub:
                                st.error("❌ Nama sub departemen harus diisi!")
                            else:
                                with st.spinner("Mengupdate data..."):
                                    success, msg = update_subdepartemen(edit_id_sub, id_dept_edit, edit_nama_sub)
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