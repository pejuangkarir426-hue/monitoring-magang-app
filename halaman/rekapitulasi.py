import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils import (
    load_data_cached, refresh_data_in_session,
    parse_time, hitung_umut, create_excel_sheet
)
from config import SPREADSHEET_ID


def halaman_Rekapitulasi_Presensi():
    tabb1, tabb2 = st.tabs(["Rekapitulasi", "Status Terbayar"])

    # ─────────────────────────────────────────────
    # TAB 1: REKAPITULASI UMUT
    # ─────────────────────────────────────────────
    with tabb1:
        st.title("📊 Rekapitulasi Presensi dan UMUT Mahasiswa Magang")

        if "rekap_ready" not in st.session_state:
            st.session_state.rekap_ready = False
        if "tgl_awal" not in st.session_state:
            st.session_state.tgl_awal = datetime.now().date()
        if "tgl_akhir" not in st.session_state:
            st.session_state.tgl_akhir = datetime.now().date()

        col1, col2 = st.columns(2)
        with col1:
            tgl_awal = st.date_input("Tanggal Awal", value=st.session_state.tgl_awal)
        with col2:
            tgl_akhir = st.date_input("Tanggal Akhir", value=st.session_state.tgl_akhir)

        if tgl_awal > tgl_akhir:
            st.error("Tanggal awal harus lebih kecil atau sama dengan tanggal akhir.")
            return

        if st.button("🚀 Proses Rekapitulasi", use_container_width=True):
            st.session_state.rekap_ready = True
            st.session_state.tgl_awal = tgl_awal
            st.session_state.tgl_akhir = tgl_akhir

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

            try:
                df_departemen = st.session_state.data_departemen.copy()
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

            df_presensi['Tanggal_dt'] = pd.to_datetime(
                df_presensi['Tanggal'], format='%d/%m/%Y', errors='coerce')
            mask = ((df_presensi['Tanggal_dt'] >= pd.Timestamp(tgl_awal)) &
                    (df_presensi['Tanggal_dt'] <= pd.Timestamp(tgl_akhir)))
            df_presensi_filter = df_presensi.loc[mask].copy()

            if df_presensi_filter.empty:
                st.warning("Tidak ada data presensi pada rentang tanggal tersebut.")
                return

            df_merged = pd.merge(
                df_presensi_filter,
                df_magang[['ID_Magang', 'Nama', 'Sub Dept', 'Bagian/Dept']],
                on='ID_Magang', how='left')

            if 'Nama_x' in df_merged.columns and 'Nama_y' in df_merged.columns:
                df_merged['Nama'] = df_merged['Nama_y']
                df_merged.drop(columns=['Nama_x', 'Nama_y'], inplace=True)

            date_range = pd.date_range(start=tgl_awal, end=tgl_akhir)
            tanggal_list = [str(d.day) for d in date_range]

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
                hasil[id_magang] = {
                    'ID_Magang': id_magang, 'Nama': nama, 'Sub Dept': sub_dept,
                    **umut_per_tgl, 'Pendapatan': total,
                    'Keterangan': "; ".join(keterangan_list)
                }

            df_hasil = pd.DataFrame.from_dict(hasil, orient='index')
            kolom_tanggal = [str(t) for t in tanggal_list]
            kolom_akhir = ['ID_Magang', 'Nama', 'Sub Dept'] + kolom_tanggal + ['Pendapatan', 'Keterangan']
            df_hasil = df_hasil[kolom_akhir]

            st.subheader(f"📋 Rekap UMUT per Departemen Periode {tgl_awal} hingga {tgl_akhir}")

            df_dept = df_magang[['ID_Magang', 'Bagian/Dept']].drop_duplicates()
            df_hasil_with_dept = df_hasil.merge(df_dept, on='ID_Magang', how='left')
            dept_list = df_hasil_with_dept['Bagian/Dept'].dropna().unique()

            if len(dept_list) == 0:
                st.warning("Tidak ada data mahasiswa dengan departemen.")
                return

            tabs = st.tabs([f"🏢 {dept}" for dept in dept_list])
            periode_str = f"Periode: {tgl_awal.strftime('%d/%m/%Y')} - {tgl_akhir.strftime('%d/%m/%Y')}"

            for tab, dept in zip(tabs, dept_list):
                with tab:
                    df_tab = df_hasil_with_dept[df_hasil_with_dept['Bagian/Dept'] == dept].drop(columns=['Bagian/Dept'])
                    st.dataframe(df_tab)
                    clm1, clm2, clm3 = st.columns(3)

                    with clm1:
                        total_pendapatan = df_tab['Pendapatan'].sum()
                        st.metric("💰 Total Pendapatan Departemen", f"Rp {total_pendapatan:,.0f}")

                    with clm3:
                        with st.popover(f"✅ Tandai {dept} Terbayar"):
                            data_terbayar = []
                            for _, row in df_tab.iterrows():
                                id_magang = row['ID_Magang']
                                for tgl in kolom_tanggal:
                                    umut = row[tgl]
                                    tgl_int = int(tgl)
                                    tgl_filter = date_range[date_range.day == tgl_int]
                                    if len(tgl_filter) > 0:
                                        tgl_target = tgl_filter[0]
                                        data_scan = df_presensi_filter[
                                            (df_presensi_filter['ID_Magang'] == id_magang) &
                                            (df_presensi_filter['Tanggal_dt'].dt.date == tgl_target.date())]
                                        if not data_scan.empty:
                                            row_scan = data_scan.iloc[0]
                                            scan_masuk = row_scan.get('Scan Masuk', '')
                                            scan_keluar = row_scan.get('Scan Keluar', '')
                                            sm_valid = not pd.isna(scan_masuk) and str(scan_masuk).strip() != ''
                                            sk_valid = not pd.isna(scan_keluar) and str(scan_keluar).strip() != ''
                                            if umut > 0 and sm_valid and sk_valid:
                                                data_terbayar.append({
                                                    'ID_Magang': id_magang, 'Tanggal': tgl,
                                                    'Tanggal_full': tgl_target.strftime('%d/%m/%Y'),
                                                    'UMUT': umut, 'Scan Masuk': scan_masuk, 'Scan Keluar': scan_keluar
                                                })

                            df_terbayar = pd.DataFrame(data_terbayar)
                            total_terbayar = len(df_terbayar)

                            st.warning(
                                f"Anda akan menandai presensi mahasiswa **{dept}** pada periode "
                                f"{tgl_awal.strftime('%d/%m/%Y')} - {tgl_akhir.strftime('%d/%m/%Y')} "
                                f"sebagai **terbayar**.\n\nTindakan ini tidak dapat dibatalkan.")

                            if st.button("Ya, tandai sekarang", key=f"confirm_bayar_{dept}"):
                                if total_terbayar == 0:
                                    st.warning("⚠️ Tidak ada data yang memenuhi kriteria untuk ditandai.")
                                else:
                                    st.info(f"Memproses update {total_terbayar} data ke Google Sheets...")
                                    try:
                                        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                                        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                                        client = gspread.authorize(creds)
                                        spreadsheet = client.open_by_key(SPREADSHEET_ID)
                                        worksheet_presensi = spreadsheet.worksheet("data_presensi")
                                        all_values = worksheet_presensi.get_all_values()
                                        if len(all_values) == 0:
                                            st.warning("Sheet data_presensi kosong.")
                                            return
                                        headers = all_values[0]
                                        try:
                                            id_col_idx = headers.index('ID_Magang')
                                            tgl_col_idx = headers.index('Tanggal')
                                            status_col_idx = headers.index('Status Terbayar')
                                        except ValueError as e:
                                            st.error(f"Kolom wajib tidak ditemukan: {e}")
                                            return
                                        lookup_set = set()
                                        for _, row in df_terbayar.iterrows():
                                            lookup_set.add((str(row['ID_Magang']), row['Tanggal_full']))
                                        updates = []
                                        updated_count = 0
                                        skipped_count = 0
                                        for i, row in enumerate(all_values[1:], start=2):
                                            if len(row) <= max(id_col_idx, tgl_col_idx):
                                                continue
                                            id_m = str(row[id_col_idx]).strip()
                                            tgl_str = row[tgl_col_idx].strip()
                                            if (id_m, tgl_str) in lookup_set:
                                                scan_masuk = row[headers.index('Scan Masuk')] if 'Scan Masuk' in headers else ''
                                                scan_keluar = row[headers.index('Scan Keluar')] if 'Scan Keluar' in headers else ''
                                                sm_valid = scan_masuk and str(scan_masuk).strip() != ''
                                                sk_valid = scan_keluar and str(scan_keluar).strip() != ''
                                                if sm_valid and sk_valid:
                                                    col_letter = gspread.utils.rowcol_to_a1(1, status_col_idx + 1)[0]
                                                    updates.append({'range': f"{col_letter}{i}", 'values': [['terbayar']]})
                                                    updated_count += 1
                                                else:
                                                    skipped_count += 1
                                        if updates:
                                            worksheet_presensi.batch_update(updates)
                                            st.success(f"✅ Berhasil mengupdate {updated_count} baris di departemen {dept}.")
                                            if skipped_count > 0:
                                                st.info(f"⏭️ {skipped_count} data dilewati karena scan kosong.")
                                            refresh_data_in_session()
                                            st.rerun()
                                        else:
                                            st.warning("Tidak ada baris presensi yang cocok dengan kriteria.")
                                    except Exception as e:
                                        st.error(f"Terjadi error: {e}")

            st.divider()
            output_all = BytesIO()
            with pd.ExcelWriter(output_all, engine='xlsxwriter') as writer:
                for dept in dept_list:
                    df_tab_dl = df_hasil_with_dept[df_hasil_with_dept['Bagian/Dept'] == dept].drop(columns=['Bagian/Dept'])
                    judul = f"Rekap UMUT - Departemen {dept}\n{periode_str}"
                    create_excel_sheet(writer, df_tab_dl, dept[:31], judul)
            output_all.seek(0)
            st.download_button(
                label="📥 Download Excel Semua Departemen", data=output_all,
                file_name=f"rekap_umut_semua_{tgl_awal.strftime('%Y%m%d')}_{tgl_akhir.strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

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

    # ─────────────────────────────────────────────
    # TAB 2: STATUS TERBAYAR
    # ─────────────────────────────────────────────
    with tabb2:
        st.title("💰 Rekapitulasi UMUT Terbayar")
        st.markdown("Menampilkan data presensi yang sudah ditandai **terbayar** berdasarkan periode dan status pembayaran")

        df_presensi = st.session_state.get('data_presensi', load_data_cached("data_presensi")).copy()
        df_magang = st.session_state.get('data_magang', load_data_cached("database_magang")).copy()

        with st.container(border=True):
            st.subheader("🔍 Filter Data")
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                status_options = ["Semua Status", "Terbayar", "Belum Terbayar"]
                filter_status = st.selectbox("Status Pembayaran", options=status_options, index=1, key="filter_status_terbayar")
            with col_f2:
                dept_options = ["Semua Departemen"] + sorted(df_magang['Bagian/Dept'].unique().tolist())
                filter_dept = st.selectbox("Departemen", options=dept_options, key="filter_dept_terbayar")
            with col_f3:
                if not df_presensi.empty and 'Tanggal' in df_presensi.columns:
                    df_presensi['Tanggal_dt_filter'] = pd.to_datetime(df_presensi['Tanggal'], format='%d/%m/%Y', errors='coerce')
                    min_date = df_presensi['Tanggal_dt_filter'].min().date() if not df_presensi['Tanggal_dt_filter'].isna().all() else datetime.now().date()
                    max_date = df_presensi['Tanggal_dt_filter'].max().date() if not df_presensi['Tanggal_dt_filter'].isna().all() else datetime.now().date()
                else:
                    min_date = max_date = datetime.now().date()
                filter_tanggal = st.date_input("Periode Tanggal", value=(min_date, max_date), key="filter_tanggal_terbayar")

        if not df_presensi.empty:
            df_presensi['Tanggal_dt'] = pd.to_datetime(df_presensi['Tanggal'], format='%d/%m/%Y', errors='coerce')
            df_display = pd.merge(df_presensi, df_magang[['ID_Magang', 'Nama', 'Bagian/Dept', 'Sub Dept']], on='ID_Magang', how='left')

            if filter_status == "Terbayar":
                df_display = df_display[df_display['Status Terbayar'].str.lower() == 'terbayar']
            elif filter_status == "Belum Terbayar":
                df_display = df_display[df_display['Status Terbayar'].isna() | (df_display['Status Terbayar'] == '') | (df_display['Status Terbayar'].str.lower() != 'terbayar')]

            if filter_dept != "Semua Departemen":
                df_display = df_display[df_display['Bagian/Dept'] == filter_dept]

            if len(filter_tanggal) == 2:
                tgl_mulai, tgl_selesai = filter_tanggal
                df_display = df_display[
                    (df_display['Tanggal_dt'] >= pd.Timestamp(tgl_mulai)) &
                    (df_display['Tanggal_dt'] <= pd.Timestamp(tgl_selesai))]

            st.divider()
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("📊 Total Data", f"{len(df_display)} baris")
            with col_m2:
                st.metric("👥 Jumlah Mahasiswa", df_display['ID_Magang'].nunique())
            with col_m3:
                total_terbayar = len(df_display[df_display['Status Terbayar'].str.lower() == 'terbayar']) if filter_status != "Terbayar" else len(df_display)
                st.metric("✅ Sudah Terbayar", total_terbayar)
            with col_m4:
                total_belum = len(df_display[df_display['Status Terbayar'].isna() | (df_display['Status Terbayar'] == '') | (df_display['Status Terbayar'].str.lower() != 'terbayar')]) if filter_status != "Belum Terbayar" else len(df_display)
                st.metric("⏳ Belum Terbayar", total_belum)

            st.divider()

            if not df_display.empty:
                display_columns = ['ID_Magang', 'Nama', 'Bagian/Dept', 'Sub Dept', 'Tanggal', 'Jam Masuk', 'Jam Pulang', 'Scan Masuk', 'Scan Keluar', 'Status Terbayar']
                available_columns = [col for col in display_columns if col in df_display.columns]
                df_show = df_display[available_columns].copy()
                if 'ID_Magang' in df_show.columns:
                    df_show['ID_Magang'] = df_show['ID_Magang'].astype(str)

                def color_status(val):
                    if pd.isna(val) or val == '':
                        return 'background-color: #ffcccc'
                    elif str(val).lower() == 'terbayar':
                        return 'background-color: #ccffcc'
                    return ''

                st.subheader("📋 Detail Data Presensi")
                st.dataframe(
                    df_show.style.applymap(color_status, subset=['Status Terbayar'] if 'Status Terbayar' in df_show.columns else []),
                    use_container_width=True, height=400)

                st.divider()
                st.subheader("📊 Rekapitulasi per Mahasiswa")
                rekap_mahasiswa = []
                for id_mhs, group in df_display.groupby('ID_Magang'):
                    nama = group['Nama'].iloc[0] if 'Nama' in group.columns else '-'
                    dept = group['Bagian/Dept'].iloc[0] if 'Bagian/Dept' in group.columns else '-'
                    subdept = group['Sub Dept'].iloc[0] if 'Sub Dept' in group.columns else '-'
                    total_hadir = len(group)
                    terbayar = len(group[group['Status Terbayar'].str.lower() == 'terbayar'])
                    rekap_mahasiswa.append({
                        'ID_Magang': str(id_mhs), 'Nama': nama, 'Departemen': dept, 'Sub Dept': subdept,
                        'Total Hadir': total_hadir, 'Sudah Terbayar': terbayar,
                        'Belum Terbayar': total_hadir - terbayar,
                        'Persentase Terbayar': f"{(terbayar/total_hadir*100):.1f}%" if total_hadir > 0 else "0%"
                    })
                df_rekap = pd.DataFrame(rekap_mahasiswa)
                st.dataframe(df_rekap, use_container_width=True, height=300)

                st.divider()
                st.subheader("📈 Visualisasi Status Terbayar")
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    status_counts = df_display['Status Terbayar'].fillna('Belum Terbayar').replace('', 'Belum Terbayar')
                    status_counts = status_counts.apply(lambda x: 'Terbayar' if str(x).lower() == 'terbayar' else 'Belum Terbayar')
                    status_data = status_counts.value_counts().reset_index()
                    status_data.columns = ['Status', 'Jumlah']
                    fig_pie = px.pie(status_data, values='Jumlah', names='Status', title="Proporsi Status Terbayar",
                                     color='Status', color_discrete_map={'Terbayar': '#4CAF50', 'Belum Terbayar': '#FF5722'}, hole=0.4)
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col_v2:
                    dept_status = df_display.copy()
                    dept_status['Status'] = dept_status['Status Terbayar'].fillna('Belum Terbayar').replace('', 'Belum Terbayar')
                    dept_status['Status'] = dept_status['Status'].apply(lambda x: 'Terbayar' if str(x).lower() == 'terbayar' else 'Belum Terbayar')
                    dept_summary = dept_status.groupby(['Bagian/Dept', 'Status']).size().reset_index(name='Jumlah')
                    fig_bar = px.bar(dept_summary, x='Bagian/Dept', y='Jumlah', color='Status',
                                     title="Status Terbayar per Departemen",
                                     color_discrete_map={'Terbayar': '#4CAF50', 'Belum Terbayar': '#FF5722'},
                                     barmode='stack', text='Jumlah')
                    fig_bar.update_traces(textposition='inside')
                    fig_bar.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)

                st.divider()
                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    output_detail = BytesIO()
                    with pd.ExcelWriter(output_detail, engine='xlsxwriter') as writer:
                        df_show.to_excel(writer, sheet_name='Detail Presensi', index=False)
                        df_rekap.to_excel(writer, sheet_name='Rekap Mahasiswa', index=False)
                        wb = writer.book
                        ws1 = writer.sheets['Detail Presensi']
                        ws2 = writer.sheets['Rekap Mahasiswa']
                        for i, col in enumerate(df_show.columns):
                            max_len = max(df_show[col].astype(str).map(len).max(), len(col)) + 2
                            ws1.set_column(i, i, max_len)
                        for i, col in enumerate(df_rekap.columns):
                            max_len = max(df_rekap[col].astype(str).map(len).max(), len(col)) + 2
                            ws2.set_column(i, i, max_len)
                    output_detail.seek(0)
                    st.download_button(
                        label="📥 Download Data Detail (Excel)", data=output_detail,
                        file_name=f"status_terbayar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_status_terbayar")

                with col_e2:
                    if filter_status != "Terbayar" and len(df_display) > 0:
                        with st.popover("✅ Tandai Semua Terbayar"):
                            st.warning(f"Anda akan menandai **{len(df_display)} data** sebagai **terbayar**. Tindakan ini tidak dapat dibatalkan.")
                            if st.button("Ya, tandai semua terbayar", key="confirm_bayar_semua"):
                                st.info("Memproses update ke Google Sheets...")
                                try:
                                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                                    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                                    client = gspread.authorize(creds)
                                    spreadsheet = client.open_by_key(SPREADSHEET_ID)
                                    worksheet_presensi = spreadsheet.worksheet("data_presensi")
                                    all_values = worksheet_presensi.get_all_values()
                                    if len(all_values) == 0:
                                        st.warning("Sheet data_presensi kosong.")
                                        return
                                    headers = all_values[0]
                                    try:
                                        id_col_idx = headers.index('ID_Magang')
                                        tgl_col_idx = headers.index('Tanggal')
                                        status_col_idx = headers.index('Status Terbayar')
                                    except ValueError as e:
                                        st.error(f"Kolom wajib tidak ditemukan: {e}")
                                        return
                                    update_set = set()
                                    for _, row in df_display.iterrows():
                                        update_set.add((str(row['ID_Magang']), row['Tanggal']))
                                    updates = []
                                    for i, row in enumerate(all_values[1:], start=2):
                                        if len(row) <= max(id_col_idx, tgl_col_idx):
                                            continue
                                        id_m = str(row[id_col_idx]).strip()
                                        tgl_str = row[tgl_col_idx].strip()
                                        if (id_m, tgl_str) in update_set:
                                            col_letter = gspread.utils.rowcol_to_a1(1, status_col_idx + 1)[0]
                                            updates.append({'range': f"{col_letter}{i}", 'values': [['terbayar']]})
                                    if updates:
                                        worksheet_presensi.batch_update(updates)
                                        st.success(f"✅ Berhasil mengupdate {len(updates)} baris presensi.")
                                        refresh_data_in_session()
                                        st.rerun()
                                    else:
                                        st.warning("Tidak ada baris presensi yang cocok dengan kriteria.")
                                except Exception as e:
                                    st.error(f"Terjadi error: {e}")

                with col_e3:
                    if st.button("🔄 Reset Filter", key="reset_filter_terbayar"):
                        st.rerun()
            else:
                st.info("📭 Tidak ada data sesuai dengan filter yang dipilih")
        else:
            st.info("📭 Belum ada data presensi")
