import streamlit as st
import pandas as pd
import plotly.express as px


# ----- Fungsi Load dan Cleaning Dataset -----

@st.cache_data
def load_data():
    df = pd.read_csv("Data/googleplaystore.csv")

    # --- Bersihkan nama kolom ---
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # --- Konversi kolom numerik ---
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce')

    # --- Bersihkan kolom installs ---
    df['installs'] = df['installs'].astype(str).str.replace('[+,]', '', regex=True)
    df['installs'] = pd.to_numeric(df['installs'], errors='coerce')

    # --- Normalisasi kolom type ---
    df['type'] = df['type'].astype(str).str.strip().str.capitalize()

    # --- Bersihkan kolom price ---
    df['price'] = df['price'].astype(str)
    df['price'] = df['price'].str.replace('$', '', regex=True)
    df['price'] = df['price'].str.replace('Free', '0', case=False, regex=False)
    df['price'] = df['price'].str.replace('Everyone', '0', case=False, regex=False)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # --- Hapus baris yang tidak relevan ---
    df = df.dropna(subset=['rating', 'installs', 'category'])

    return df



# --- Load Dataset
df_GPlayStore = load_data()



# ----- Tampilan Awal Dashboard -----
st.set_page_config(page_title="Google Play Store Dashboard", layout="wide")

st.title("📱 Google Play Store Dashboard")
st.caption("Analisis data aplikasi berdasarkan kategori, rating, dan harga.")

# KPI Section
col1, col2, col3 = st.columns(3)
col1.metric("Jumlah Aplikasi", f"{len(df_GPlayStore):,}")
col2.metric("Rata-rata Rating", f"{df_GPlayStore['rating'].mean():.2f}")
col3.metric("Kategori Unik", df_GPlayStore['category'].nunique())

# Data preview (disembunyikan agar dashboard rapi)
with st.expander("🔍 Lihat 5 Baris Pertama Data"):
    st.dataframe(df_GPlayStore.head())



# ----- Sidebar Filter -----

st.sidebar.header("🔎 Filter Data")

category_list = ['All'] + sorted(df_GPlayStore['category'].unique())
category_filter = st.sidebar.selectbox("Pilih Kategori", category_list)

type_list = ['All'] + sorted(df_GPlayStore['type'].dropna().unique())
type_filter = st.sidebar.selectbox("Pilih Tipe Aplikasi", type_list)

filtered_df = df_GPlayStore.copy()

if category_filter != 'All':
    filtered_df = filtered_df[filtered_df['category'] == category_filter]
if type_filter != 'All':
    filtered_df = filtered_df[filtered_df['type'] == type_filter]


# ----- KPI Berdasarkan Filter -----
avg_rating = filtered_df['rating'].mean()
total_downloads = filtered_df['installs'].sum()
avg_price = filtered_df[filtered_df['type'].str.strip().str.lower() == 'paid']['price'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("⭐ Rata-rata Rating", f"{avg_rating:.2f}")
col2.metric("⬇️ Total Downloads", f"{total_downloads:,.0f}")
col3.metric("💰 Rata-rata Harga (Paid)", f"${avg_price:.2f}" if not pd.isna(avg_price) else "$0.00")


# ----- Visualisasi Data -----

# Distribusi Rating
st.subheader("📊 Distribusi Rating Aplikasi")
fig_rating = px.histogram(
    filtered_df,
    x='rating',
    nbins=20,
    title="Distribusi Rating Aplikasi",
    color_discrete_sequence=['#0083B8']
)
st.plotly_chart(fig_rating, use_container_width=True)

#  Total Download per Kategori
st.subheader("🏷️ Total Download per Kategori")
cat_downloads = (
    filtered_df.groupby('category')['installs']
    .sum()
    .reset_index()
    .sort_values(by='installs', ascending=False)
)
fig_download = px.bar(
    cat_downloads,
    x='category',
    y='installs',
    color='category',
    title="Total Download per Kategori"
)
st.plotly_chart(fig_download, use_container_width=True)

# Harga Rata-rata per Kategori (Paid Apps)
st.subheader("💵 Harga Rata-rata per Kategori (Paid Apps)")
paid_apps = filtered_df[filtered_df['type'].str.strip().str.lower() == 'paid']
if not paid_apps.empty:
    avg_price_cat = (
        paid_apps.groupby('category')['price']
        .mean()
        .reset_index()
        .sort_values(by='price', ascending=False)
    )
    fig_price = px.bar(
        avg_price_cat,
        x='category',
        y='price',
        color='category',
        title="Harga Rata-rata per Kategori"
    )
    st.plotly_chart(fig_price, use_container_width=True)
else:
    st.info("Tidak ada aplikasi berbayar dalam filter saat ini.")

#  Top 10 Aplikasi dengan Rating Tertinggi
st.subheader("🔥 Top 10 Aplikasi dengan Rating Tertinggi")
top_apps = filtered_df.sort_values(by='rating', ascending=False).head(10)
st.dataframe(top_apps[['app', 'category', 'rating', 'installs', 'type', 'price']])