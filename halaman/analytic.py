import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import convert_tanggal


def halaman_Magang_Analytic():
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
                fig1 = px.pie(status_counts, values='Jumlah', names='Status', hole=0.4,
                              color_discrete_sequence=px.colors.qualitative.Set3,
                              title="Distribusi Status Magang")
                fig1.update_traces(textposition='inside', textinfo='percent+label')
                fig1.update_layout(title_x=0.3, height=400)
                st.plotly_chart(fig1, use_container_width=True)

        with col2:
            with st.container(border=True):
                jk_counts = df['Jenis Kelamin'].value_counts().reset_index()
                jk_counts.columns = ['Jenis Kelamin', 'Jumlah']
                fig2 = px.pie(jk_counts, values='Jumlah', names='Jenis Kelamin', hole=0.4,
                              title="Proporsi Jenis Kelamin", color='Jenis Kelamin',
                              color_discrete_map={'Laki-laki': '#2E86AB', 'Perempuan': '#A23B72'})
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                fig2.update_layout(title_x=0.3, height=400)
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                df_sekolah = df[df['Jenis Univ/Sekolah'] == "Sekolah"]
                sekolah_counts = df_sekolah['Sekolah/Universitas'].value_counts().reset_index()
                sekolah_counts.columns = ['Sekolah', 'Jumlah']
                fig_sekolah = px.bar(sekolah_counts, y='Sekolah', x='Jumlah', orientation='h',
                                     text='Jumlah', color='Jumlah', color_continuous_scale='Cividis',
                                     title="Sekolah Pengirim Magang Terbanyak")
                fig_sekolah.update_traces(textposition='outside')
                fig_sekolah.update_layout(height=500, yaxis={'categoryorder': 'total ascending'}, title_x=0.3)
                st.plotly_chart(fig_sekolah, use_container_width=True)

        with col2:
            with st.container(border=True):
                df_univ = df[df['Jenis Univ/Sekolah'] == "Universitas"]
                univ_counts = df_univ['Sekolah/Universitas'].value_counts().reset_index()
                univ_counts.columns = ['Universitas', 'Jumlah']
                fig_univ = px.bar(univ_counts, y='Universitas', x='Jumlah', orientation='h',
                                  text='Jumlah', color='Jumlah', color_continuous_scale='Viridis',
                                  title="Universitas Pengirim Magang Terbanyak")
                fig_univ.update_traces(textposition='outside')
                fig_univ.update_layout(height=500, yaxis={'categoryorder': 'total ascending'}, title_x=0.3)
                st.plotly_chart(fig_univ, use_container_width=True)

        st.markdown("---")

        col3, col4 = st.columns(2)
        with col3:
            with st.container(border=True):
                dept_counts = df['Bagian/Dept'].value_counts().reset_index()
                dept_counts.columns = ['Departemen', 'Jumlah']
                fig4 = px.bar(dept_counts, x='Departemen', y='Jumlah', color='Jumlah', text='Jumlah',
                              color_continuous_scale='Plasma', title="Jumlah Magang per Departemen")
                fig4.update_traces(textposition='outside')
                fig4.update_layout(height=450, title_x=0.3, xaxis_tickangle=-45)
                st.plotly_chart(fig4, use_container_width=True)

        with col4:
            with st.container(border=True):
                dept_status = pd.crosstab(df['Bagian/Dept'], df['S/A/SB/OP/DT'])
                dept_status_melted = dept_status.reset_index().melt(id_vars='Bagian/Dept', var_name='Status', value_name='Jumlah')
                fig5 = px.bar(dept_status_melted, x='Bagian/Dept', y='Jumlah', color='Status', text='Jumlah',
                              barmode='stack', color_discrete_sequence=px.colors.qualitative.Set2,
                              title="Status Magang per Departemen")
                fig5.update_traces(textposition='inside')
                fig5.update_layout(height=450, title_x=0.3, xaxis_tickangle=-45)
                st.plotly_chart(fig5, use_container_width=True)

        st.markdown("---")

        df['Mulai'] = df['Mulai'].apply(convert_tanggal)
        df['Akhir'] = df['Akhir'].apply(convert_tanggal)

        df_mulai = df.dropna(subset=['Mulai']).copy()
        df_mulai['Bulan'] = df_mulai['Mulai'].dt.to_period('M')
        trend_mulai = df_mulai.groupby('Bulan').size().reset_index(name='Jumlah')
        trend_mulai['Bulan'] = trend_mulai['Bulan'].astype(str)

        df_akhir = df.dropna(subset=['Akhir']).copy()
        df_akhir['Bulan'] = df_akhir['Akhir'].dt.to_period('M')
        trend_akhir = df_akhir.groupby('Bulan').size().reset_index(name='Jumlah')
        trend_akhir['Bulan'] = trend_akhir['Bulan'].astype(str)

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                fig1 = px.line(trend_mulai, x='Bulan', y='Jumlah', markers=True, title="Trend Mulai Magang per Bulan")
                fig1.update_traces(mode="lines+markers", marker=dict(size=10), line=dict(width=3))
                fig1.update_layout(title_x=0.3, height=450, xaxis_title="Bulan", yaxis_title="Jumlah Peserta")
                st.plotly_chart(fig1, use_container_width=True)

        with col2:
            with st.container(border=True):
                fig2 = px.line(trend_akhir, x='Bulan', y='Jumlah', markers=True, title="Trend Akhir Magang per Bulan")
                fig2.update_traces(mode="lines+markers", marker=dict(size=10), line=dict(width=3))
                fig2.update_layout(title_x=0.3, height=450, xaxis_title="Bulan", yaxis_title="Jumlah Peserta")
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        sunburst_data = df.groupby(['S/A/SB/OP/DT', 'Bagian/Dept', 'Sekolah/Universitas']).size().reset_index(name='Jumlah')
        fig10 = px.sunburst(sunburst_data, path=['S/A/SB/OP/DT', 'Bagian/Dept', 'Sekolah/Universitas'],
                            values='Jumlah', title='Hierarki: Status → Departemen → Universitas',
                            color='Jumlah', color_continuous_scale='Viridis')
        fig10.update_layout(height=800, title_x=0.36)
        st.plotly_chart(fig10, use_container_width=True)
        st.markdown("---")

    with tab2:
        st.title("Data Magang")

        with st.container(border=True):
            st.markdown("##### 🔍 Filter Data")
            col_filter1, col_filter2, col_filter3 = st.columns(3)

            with col_filter1:
                search_nama = st.text_input("Cari Nama", placeholder="Masukkan nama...", key="filter_nama_tab2")
            with col_filter2:
                dept_options = ['Semua'] + sorted(df['Bagian/Dept'].unique().tolist())
                filter_dept = st.selectbox("Bagian/Dept", options=dept_options, key="filter_dept_tab2")
            with col_filter3:
                jenis_options = ['Semua', 'Universitas', 'Sekolah']
                filter_jenis = st.selectbox("Jenis Institusi", options=jenis_options, key="filter_jenis_tab2")

        df_filtered = df.copy()
        if search_nama:
            df_filtered = df_filtered[df_filtered['Nama'].astype(str).str.contains(search_nama, case=False, na=False)]
        if filter_dept and filter_dept != 'Semua':
            df_filtered = df_filtered[df_filtered['Bagian/Dept'] == filter_dept]
        if filter_jenis and filter_jenis != 'Semua':
            df_filtered = df_filtered[df_filtered['Jenis Univ/Sekolah'] == filter_jenis]
            
        st.markdown("---")

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

        if not df_filtered.empty:
            df_display = df_filtered.copy()
            if 'ID_Magang' in df_display.columns:
                df_display['ID_Magang'] = df_display['ID_Magang'].astype(str)

            st.dataframe(df_display, height=600, use_container_width=True, column_config={
                "ID_Magang": "ID Magang", "Nama": "Nama Lengkap", "Jenis Kelamin": "JK",
                "Jurusan/Fakultas": "Jurusan", "Jenjang": "Jenjang", "Sekolah/Universitas": "Institusi",
                "Jenis Univ/Sekolah": "Jenis", "Bagian/Dept": "Departemen", "Sub Dept": "Sub Dept",
                "Bulan": "Durasi", "Mulai": "Tgl Mulai", "Akhir": "Tgl Akhir",
                "Periode": "Periode", "Tahun": "Tahun", "Keterangan": "Ket",
                "Catatan": "Catatan", "S/A/SB/OP/DT": "Status"
            })

            st.divider()
            st.markdown("##### Statistik Data Terfilter")
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                st.metric("Total Data", len(df_filtered))
            with col_stat2:
                if 'Jenis Kelamin' in df_filtered.columns:
                    st.metric("Laki-laki", (df_filtered['Jenis Kelamin'] == 'Laki-laki').sum())
            with col_stat3:
                if 'Jenis Kelamin' in df_filtered.columns:
                    st.metric("Perempuan", (df_filtered['Jenis Kelamin'] == 'Perempuan').sum())
            with col_stat4:
                if 'S/A/SB/OP/DT' in df_filtered.columns:
                    st.metric("Aktif", (df_filtered['S/A/SB/OP/DT'] == 'On Going').sum())

            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            with col_dl2:
                csv = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv,
                    file_name=f"data_magang_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.warning("⚠️ Tidak ada data yang sesuai dengan filter")
            if df.empty:
                st.info("📭 Database magang kosong")
            else:
                st.info("📭 Coba atur ulang filter untuk melihat data")
