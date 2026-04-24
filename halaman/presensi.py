import streamlit as st
import pandas as pd
from datetime import datetime, time
import time as tm
from utils import (
    load_data, load_data_cached, append_to_sheet,
    validasi_data, refresh_data_in_session, hapus_data_by_periode
)


def halaman_Update_Presensi():
    tab11, tab22, tab33 = st.tabs(["Input Data Presensi", "Perbarui Data Presensi", "Data Presensi"])

    # ─────────────────────────────────────────────
    # TAB 11: INPUT DATA PRESENSI (UPLOAD EXCEL)
    # ─────────────────────────────────────────────
    with tab11:
        st.title("🟢 Sistem Input Data Presensi")
        st.markdown("**Ketentuan Upload File**")
        st.markdown("""
        1. File harus berformat **.xlsx** atau **.xls**  
        2. Kolom harus sesuai dengan format berikut
        """)

        st.markdown("**Kolom yang diperlukan:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("- ID_Magang\n- Nama\n- Tanggal\n- Jam Masuk")
        with col2:
            st.markdown("- Jam Pulang\n- Scan Masuk\n- Scan Keluar\n- Terlambat")
        with col3:
            st.markdown("- Plg Cpt\n- Lembur\n- Jam Kerja\n- Jml Hadir")

        st.markdown("---")

        db_data_presensi = load_data("data_presensi")
        db_magang = load_data("database_magang")

        upload_data_absen = st.file_uploader("Pilih file Excel", type=["xlsx", "xls"])

        if 'df_absen' not in st.session_state:
            st.session_state.df_absen = None
        if 'hasil_validasi' not in st.session_state:
            st.session_state.hasil_validasi = None

        if upload_data_absen is not None:
            df_absen = pd.read_excel(upload_data_absen)
            df_absen.columns = [str(col).strip() for col in df_absen.columns]
            if 'ID_Magang' in df_absen.columns:
                df_absen['ID_Magang'] = pd.to_numeric(df_absen['ID_Magang'], errors='coerce').fillna(0).astype(int)
                if (df_absen['ID_Magang'] == 0).any():
                    st.warning("⚠️ Beberapa ID_Magang tidak valid dan diganti 0. Harap periksa kembali data Anda.")
            st.session_state.df_absen = df_absen
            st.session_state.hasil_validasi = None

        if st.session_state.df_absen is not None:
            df_absen = st.session_state.df_absen
            db_data_presensi.columns = [str(col).strip() for col in db_data_presensi.columns]

            kolom_excel = list(df_absen.columns)
            kolom_database = list(db_data_presensi.columns)
            exclude_col = "Status Terbayar"
            kolom_database_tanpa_exclude = [col for col in kolom_database if col != exclude_col]

            if kolom_excel == kolom_database_tanpa_exclude:
                st.success("✅ Struktur kolom sesuai dengan database (tanpa kolom Status Terbayar)")
                st.write("Data yang diupload:")
                df_absen_tampil = df_absen.copy()
                df_absen_tampil["ID_Magang"] = df_absen_tampil["ID_Magang"].astype(str)
                st.dataframe(df_absen_tampil, use_container_width=True, height=200)

                if st.session_state.hasil_validasi is None:
                    with st.spinner("Memvalidasi data..."):
                        hasil = validasi_data(df_absen, db_magang, db_data_presensi)
                        st.session_state.hasil_validasi = hasil

                hasil = st.session_state.hasil_validasi
                st.write(f"**Data valid:** {len(hasil['valid'])} baris")
                st.write(f"**Data gagal:** {len(hasil['gagal'])} baris")

                if hasil['gagal']:
                    st.error("Detail data gagal:")
                    df_gagal = pd.DataFrame(hasil['gagal'])
                    df_gagal_tampil = df_gagal.copy()
                    df_gagal_tampil["ID_Magang"] = df_gagal_tampil["ID_Magang"].astype(str)
                    st.dataframe(df_gagal_tampil)

                if hasil['valid']:
                    if st.button("Simpan Data Valid ke Database", type='primary'):
                        col_order = kolom_database
                        data_baru = []
                        for row_dict in hasil['valid']:
                            baris = []
                            for col in col_order:
                                if col == exclude_col:
                                    val = ''
                                else:
                                    val = row_dict.get(col, '')
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
                            st.success(f"✅ Berhasil menyimpan {len(data_baru)} data ke database.")
                            st.session_state.hasil_validasi = None
                            st.session_state.df_absen = None
                            db_data_presensi = load_data("data_presensi")
                            refresh_data_in_session()
                            db_data_presensi.columns = [str(col).strip() for col in db_data_presensi.columns]
                            st.dataframe(db_data_presensi, use_container_width=True, height=200)
                        except Exception as e:
                            st.error(f"❌ Gagal menyimpan ke database: {e}")
            else:
                st.error("❌ Struktur kolom tidak sama dengan database (Status Terbayar dikecualikan)")
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

    # ─────────────────────────────────────────────
    # TAB 22: HAPUS DATA PRESENSI
    # ─────────────────────────────────────────────
    with tab22:
        st.title("🗑️ Hapus Data Presensi")
        st.markdown("**Hapus data presensi berdasarkan periode tanggal**")
        st.warning("""
        ⚠️ **PERHATIAN:**
        - Fitur ini akan **MENGHAPUS PERMANEN** data presensi
        - Data yang dihapus **TIDAK DAPAT DIKEMBALIKAN**
        - Harap periksa periode dengan teliti sebelum menghapus
        """)

        db_data_presensi = st.session_state.get('data_presensi', load_data_cached("data_presensi"))
        db_magang = st.session_state.get('data_magang', load_data_cached("database_magang"))

        with st.expander("📋 Preview Data Presensi Saat Ini", expanded=False):
            if not db_data_presensi.empty:
                sample_data = db_data_presensi.head(10).copy()
                if 'ID_Magang' in sample_data.columns:
                    sample_data['ID_Magang'] = sample_data['ID_Magang'].astype(str)
                st.dataframe(sample_data, use_container_width=True)
                st.caption(f"Total data: {len(db_data_presensi)} baris (menampilkan 10 sample)")
            else:
                st.info("Database presensi kosong")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            tgl_awal_hapus = st.date_input("📅 Tanggal Awal Periode", value=datetime.now().date(),
                                           key="tgl_awal_hapus", format="DD/MM/YYYY")
        with col2:
            tgl_akhir_hapus = st.date_input("📅 Tanggal Akhir Periode", value=datetime.now().date(),
                                            key="tgl_akhir_hapus", format="DD/MM/YYYY")

        if tgl_awal_hapus > tgl_akhir_hapus:
            st.error("❌ Tanggal awal harus lebih kecil atau sama dengan tanggal akhir!")
            st.stop()

        if not db_data_presensi.empty:
            db_data_presensi['Tanggal_dt'] = pd.to_datetime(
                db_data_presensi['Tanggal'], format='%d/%m/%Y', errors='coerce')
            mask = ((db_data_presensi['Tanggal_dt'] >= pd.Timestamp(tgl_awal_hapus)) &
                    (db_data_presensi['Tanggal_dt'] <= pd.Timestamp(tgl_akhir_hapus)))
            data_terfilter = db_data_presensi.loc[mask].copy()
            jumlah_terfilter = len(data_terfilter)
            tgl_awal_str = tgl_awal_hapus.strftime('%d/%m/%Y')
            tgl_akhir_str = tgl_akhir_hapus.strftime('%d/%m/%Y')

            st.info(f"📊 Ditemukan **{jumlah_terfilter}** data presensi pada periode **{tgl_awal_str} - {tgl_akhir_str}**")

            if jumlah_terfilter > 0:
                with st.expander("👀 Preview Data yang Akan Dihapus", expanded=True):
                    data_preview = data_terfilter.copy()
                    if 'ID_Magang' in data_preview.columns:
                        data_preview['ID_Magang'] = data_preview['ID_Magang'].astype(str)
                    if 'Tanggal_dt' in data_preview.columns:
                        data_preview = data_preview.drop(columns=['Tanggal_dt'])
                    if jumlah_terfilter > 50:
                        st.warning(f"Menampilkan 50 dari {jumlah_terfilter} data")
                        st.dataframe(data_preview.head(50), use_container_width=True)
                    else:
                        st.dataframe(data_preview, use_container_width=True)

                    if 'Bagian/Dept' in data_terfilter.columns:
                        dept_summary = data_terfilter['Bagian/Dept'].value_counts().reset_index()
                        dept_summary.columns = ['Departemen', 'Jumlah']
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write("**Ringkasan per Departemen:**")
                            st.dataframe(dept_summary, use_container_width=True)
                        with col_b:
                            id_summary = data_terfilter['ID_Magang'].value_counts().reset_index().head(10)
                            id_summary.columns = ['ID_Magang', 'Jumlah']
                            id_summary['ID_Magang'] = id_summary['ID_Magang'].astype(str)
                            st.write("**Top 10 ID Magang:**")
                            st.dataframe(id_summary, use_container_width=True)

                st.divider()
                st.error("⚠️ **KONFIRMASI PENGHAPUSAN**")
                st.write(f"Anda akan menghapus **{jumlah_terfilter}** data presensi secara permanen!")
                st.write(f"Periode: **{tgl_awal_str} - {tgl_akhir_str}**")

                confirm1 = st.checkbox("Saya memahami bahwa data yang dihapus tidak dapat dikembalikan")
                confirm2 = st.checkbox(f"Saya yakin akan menghapus {jumlah_terfilter} data pada periode tersebut")
                st.caption("🔒 Untuk keamanan, masukkan password admin")
                password_confirm = st.text_input("Password:", type="password", key="password_hapus")

                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    if st.button("🗑️ HAPUS DATA PERMANEN", use_container_width=True, type="primary",
                                 disabled=not (confirm1 and confirm2 and password_confirm == "admin123")):
                        with st.spinner(f"Menghapus {jumlah_terfilter} data..."):
                            try:
                                success, message, jumlah_hapus = hapus_data_by_periode(
                                    "data_presensi", tgl_awal_hapus, tgl_akhir_hapus)
                                if success:
                                    st.success(f"✅ **BERHASIL!** {message}")
                                    refresh_data_in_session()
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

    # ─────────────────────────────────────────────
    # TAB 33: LIHAT DATA PRESENSI
    # ─────────────────────────────────────────────
    with tab33:
        st.title("📋 Data Presensi Saat Ini")

        with st.container(border=True):
            st.markdown("##### 📅 Filter Periode Tanggal")
            col_periode1, col_periode2, col_periode3 = st.columns([2, 2, 1])

            with col_periode1:
                if 'filter_tgl_awal' not in st.session_state:
                    st.session_state.filter_tgl_awal = None
                tgl_awal_filter = st.date_input("Tanggal Awal", value=None,
                                                key="filter_tgl_awal_tab33", format="DD/MM/YYYY")
            with col_periode2:
                if 'filter_tgl_akhir' not in st.session_state:
                    st.session_state.filter_tgl_akhir = None
                tgl_akhir_filter = st.date_input("Tanggal Akhir", value=None,
                                                 key="filter_tgl_akhir_tab33", format="DD/MM/YYYY")
            with col_periode3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Reset", use_container_width=True, key="reset_periode_tab33"):
                    st.session_state.filter_tgl_awal_tab33 = None
                    st.session_state.filter_tgl_akhir_tab33 = None
                    st.rerun()

        db_data_presensi_tampil = db_data_presensi.copy()
        if not db_data_presensi_tampil.empty and 'Tanggal' in db_data_presensi_tampil.columns:
            db_data_presensi_tampil['Tanggal_dt'] = pd.to_datetime(
                db_data_presensi_tampil['Tanggal'], format='%d/%m/%Y', errors='coerce')

        df_filtered = db_data_presensi_tampil.copy()

        if tgl_awal_filter and tgl_akhir_filter:
            if tgl_awal_filter > tgl_akhir_filter:
                st.error("❌ Tanggal awal harus lebih kecil atau sama dengan tanggal akhir!")
            else:
                mask = ((df_filtered['Tanggal_dt'] >= pd.Timestamp(tgl_awal_filter)) &
                        (df_filtered['Tanggal_dt'] <= pd.Timestamp(tgl_akhir_filter)))
                df_filtered = df_filtered.loc[mask].copy()
                tgl_awal_str = tgl_awal_filter.strftime('%d/%m/%Y')
                tgl_akhir_str = tgl_akhir_filter.strftime('%d/%m/%Y')
                st.info(f"📊 Menampilkan data periode **{tgl_awal_str} - {tgl_akhir_str}**")
        elif tgl_awal_filter or tgl_akhir_filter:
            st.warning("⚠️ Harap isi kedua tanggal awal dan akhir untuk filter periode")

        for col in ["Status Terbayar", "Tanggal_dt"]:
            if col in df_filtered.columns:
                df_filtered = df_filtered.drop(columns=[col])
        if 'ID_Magang' in df_filtered.columns:
            df_filtered["ID_Magang"] = df_filtered["ID_Magang"].astype(str)

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Total Data", len(df_filtered))
        with col_info2:
            if not df_filtered.empty and 'ID_Magang' in df_filtered.columns:
                st.metric("Jumlah Mahasiswa", df_filtered['ID_Magang'].nunique())
        with col_info3:
            if not df_filtered.empty and 'Tanggal' in df_filtered.columns:
                try:
                    tanggal_dt = pd.to_datetime(df_filtered['Tanggal'], format='%d/%m/%Y', errors='coerce')
                    tgl_min = tanggal_dt.min().strftime('%d/%m/%Y') if pd.notna(tanggal_dt.min()) else '-'
                    tgl_max = tanggal_dt.max().strftime('%d/%m/%Y') if pd.notna(tanggal_dt.max()) else '-'
                    st.metric("Rentang Tanggal", f"{tgl_min} - {tgl_max}")
                except:
                    st.metric("Rentang Tanggal", "-")

        st.divider()

        if not df_filtered.empty:
            st.dataframe(df_filtered, height=600, use_container_width=True, column_config={
                "ID_Magang": "ID Magang", "Tanggal": "Tanggal",
                "Jam Masuk": "Jam Masuk", "Jam Pulang": "Jam Pulang",
                "Scan Masuk": "Scan Masuk", "Scan Keluar": "Scan Keluar",
                "Terlambat": "Terlambat", "Plg Cpt": "Pulang Cepat",
                "Lembur": "Lembur", "Jam Kerja": "Jam Kerja", "Jml Hadir": "Jml Hadir"
            })

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
                        df_filtered['Bulan'] = pd.to_datetime(
                            df_filtered['Tanggal'], format='%d/%m/%Y', errors='coerce').dt.month
                        bulan_summary = df_filtered.groupby('Bulan').size().reset_index()
                        bulan_summary.columns = ['Bulan', 'Jumlah']
                        nama_bulan = {1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
                                      5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
                                      9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'}
                        bulan_summary['Bulan'] = bulan_summary['Bulan'].map(nama_bulan)
                        st.dataframe(bulan_summary, use_container_width=True, height=200)
                        df_filtered = df_filtered.drop(columns=['Bulan'], errors='ignore')

            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            with col_dl2:
                csv_data = df_filtered.to_csv(index=False).encode('utf-8')
                if tgl_awal_filter and tgl_akhir_filter:
                    periode_str = f"{tgl_awal_filter.strftime('%Y%m%d')}_{tgl_akhir_filter.strftime('%Y%m%d')}"
                else:
                    periode_str = "semua"
                st.download_button(
                    label="📥 Download Data (CSV)", data=csv_data,
                    file_name=f"data_presensi_{periode_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv", use_container_width=True, key="download_presensi_tab33")
        else:
            st.warning("⚠️ Tidak ada data presensi pada periode yang dipilih")
            if db_data_presensi.empty:
                st.info("📭 Database presensi masih kosong")
            else:
                st.info("📭 Tidak ada data pada periode filter. Coba atur ulang filter.")
