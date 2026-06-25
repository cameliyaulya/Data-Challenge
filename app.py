import streamlit as st
import pandas as pd
import plotly.express as px  # Digunakan untuk membuat histogram & boxplot interaktif

# 1. Setup Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Deka Insight - Advanced Dashboard", layout="wide")

st.title("📊 Deka Insight: Advanced Norm & Score Dashboard")
st.markdown("Dashboard interaktif untuk memonitor Norm Data dan Distribusi Skor Aktual Responden.")

# 2. Fungsi Load Data (Menggunakan Cache)
@st.cache_data
def load_data():
    norm_df = pd.read_excel("norm_result.xlsx")
    master_df = pd.read_excel("master_response.xlsx")
    return norm_df, master_df

norm_df, master_df = load_data()

# 3. Setup Sidebar untuk Filter Interaktif
st.sidebar.header("⚙️ Filter Utama")

# Filter 1: Pilih Parameter
parameter_list = norm_df['parameter_clean'].dropna().unique().tolist()
selected_parameter = st.sidebar.selectbox("1. Pilih Parameter Uji:", parameter_list)

# Filter 2: Pilih Skala (Menyesuaikan otomatis dengan parameter)
available_scales = norm_df[norm_df['parameter_clean'] == selected_parameter]['scale'].unique().tolist()
selected_scale = st.sidebar.selectbox("2. Pilih Skala Pengukuran:", available_scales)

# Filter 3: Filter Berdasarkan Rentang Skor Aktual Responden
st.sidebar.subheader("🎯 Filter Rentang Skor")
min_score = int(master_df['score'].min())
max_score = int(master_df['score'].max())
selected_score_range = st.sidebar.slider(
    "Batasi Skor Responden di Grafik/Tabel:",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score)
)

# Proses Pemfilteran Dataset
filtered_norm = norm_df[
    (norm_df['parameter_clean'] == selected_parameter) & 
    (norm_df['scale'] == selected_scale)
]

filtered_master = master_df[
    (master_df['parameter_clean'] == selected_parameter) &
    (master_df['scale'] == selected_scale)
]

# Terapkan filter rentang skor dari slider ke data master responden
filtered_master_score = filtered_master[
    (filtered_master['score'] >= selected_score_range[0]) &
    (filtered_master['score'] <= selected_score_range[1])
]

# 4. Tampilan Konten Utama
st.subheader(f"📋 Hasil Analisis: **{selected_parameter.title()}** (Skala {selected_scale})")

if not filtered_norm.empty:
    # Menampilkan KPI Ringkasan Metrik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏆 Top 25% (Mean)", round(filtered_norm['top25_mean_score'].iloc[0], 2))
        st.caption(f"Top Box: {filtered_norm['top25_tb'].iloc[0]}% | T2B: {filtered_norm['top25_t2b'].iloc[0]}%")
    with col2:
        st.metric("➖ Mid 50% (Mean)", round(filtered_norm['mid50_mean_score'].iloc[0], 2))
        st.caption(f"Top Box: {filtered_norm['mid50_tb'].iloc[0]}% | T2B: {filtered_norm['mid50_t2b'].iloc[0]}%")
    with col3:
        st.metric("📉 Bottom 25% (Mean)", round(filtered_norm['bot25_mean_score'].iloc[0], 2))
        st.caption(f"Top Box: {filtered_norm['bot25_tb'].iloc[0]}% | T2B: {filtered_norm['bot25_t2b'].iloc[0]}%")

    st.divider()

    # 5. Bagian Visualisasi Grafik (Menggunakan Fitur Tab)
    st.subheader("📈 Analisis Visual & Distribusi Data")
    
    tab1, tab2, tab3 = st.tabs(["📊 Bar Chart (Norm)", "🎯 Histogram (Distribusi Skor)", "📦 Boxplot (Sebaran per Produk)"])
    
    with tab1:
        st.markdown("### Perbandingan Rangkuman Skor Norm Pasar")
        # Menyiapkan data barchart norm
        grafik_norm = pd.DataFrame({
            "Segmen": ["Top 25%", "Mid 50%", "Bottom 25%"],
            "Mean Score": [
                filtered_norm['top25_mean_score'].iloc[0],
                filtered_norm['mid50_mean_score'].iloc[0],
                filtered_norm['bot25_mean_score'].iloc[0]
            ],
            "Top Box (%)": [
                filtered_norm['top25_tb'].iloc[0],
                filtered_norm['mid50_tb'].iloc[0],
                filtered_norm['bot25_tb'].iloc[0]
            ]
        }).set_index("Segmen")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Barchart Rata-rata Nilai (Mean Score)**")
            st.bar_chart(grafik_norm[["Mean Score"]], color="#1f77b4")
        with c2:
            st.markdown("**Barchart Nilas Sempurna (Top Box %)**")
            st.bar_chart(grafik_norm[["Top Box (%)"]], color="#ff7f0e")

    with tab2:
        st.markdown("### Histogram Sebaran Skor Responden")
        st.caption("Menunjukkan frekuensi atau seberapa banyak responden yang memilih skor tertentu.")
        if not filtered_master_score.empty:
            fig_hist = px.histogram(
                filtered_master_score, 
                x="score", 
                nbins=int(selected_scale),
                title=f"Histogram Skor untuk Parameter: {selected_parameter}",
                labels={"score": "Skor Aktual yang Diberikan", "count": "Jumlah Responden"},
                color_discrete_sequence=["#2ca02c"]
            )
            fig_hist.update_layout(bargap=0.1, yaxis_title="Jumlah Responden")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.warning("Tidak ada data responden dalam rentang skor yang Anda pilih di sidebar.")

    with tab3:
        st.markdown("### Boxplot Distribusi Skor Berdasarkan Produk")
        st.caption("Menampilkan nilai median, kuartil bawah/atas, serta keberadaan nilai ekstrem (outlier) skor tiap produk.")
        if not filtered_master_score.empty:
            fig_box = px.box(
                filtered_master_score, 
                x="sheet_name", 
                y="score",
                title=f"Boxplot Distribusi Skor per Nama Produk ({selected_parameter})",
                labels={"sheet_name": "Kategori Produk (Sheet)", "score": "Skor Aktual"},
                color="sheet_name"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("Tidak ada data responden dalam rentang skor yang Anda pilih di sidebar.")

else:
    st.warning("Kombinasi parameter dan skala tidak ditemukan dalam database.")

st.divider()

# 6. Detail Data Mentah di bagian paling bawah
with st.expander("🔍 Lihat Detail Tabel Data Mentah Terfilter (Maksimal 200 baris)"):
    st.dataframe(filtered_master_score.head(200), use_container_width=True)