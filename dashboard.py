import streamlit as st
import pandas as pd

df = pd.read_csv(r"C:\Users\BVT-\Downloads\data-1749527924996.csv", sep=',')         # data utama dengan kolom user_id
user_df = pd.read_excel(r"C:\Users\BVT-\OneDrive - bvarta.com\BIG DATA - Project 2025\Project ~ LOKASI DataMark\Documentation\Reg User - LOKASI DataMark.xlsx")  # data user dengan user_id, email, nama, main_role

collect_count = df['collection_user_id'].value_counts().reset_index()
collect_count.columns = ['user_id', 'jumlah_collect']

label_count = df['labeling_user_id'].value_counts().reset_index()
label_count.columns = ['user_id', 'jumlah_label']

# Gabungkan kedua jumlah
user_activity = pd.merge(collect_count, label_count, on='user_id', how='outer').fillna(0)
user_activity['jumlah_collect'] = user_activity['jumlah_collect'].astype(int)
user_activity['jumlah_label'] = user_activity['jumlah_label'].astype(int)

# Gabungkan dengan data user
final_df = pd.merge(user_activity, user_df, on='user_id', how='left')

# Tambahkan total aktivitas
final_df['total_aktivitas'] = final_df['jumlah_collect'] + final_df['jumlah_label']

# Sidebar filter berdasarkan email
st.sidebar.title("Filter Email")
selected_email = st.sidebar.selectbox("Pilih Email", final_df['email'].dropna().unique())

# Data pengguna terpilih
selected_user = final_df[final_df['email'] == selected_email].iloc[0]

# Tampilkan hasil
st.title("Dashboard Aktivitas LOKASI DataMark")
st.write(f"**Nama:** {selected_user['name']}")
st.write(f"**Email:** {selected_user['email']}")
st.write(f"**Main Role:** {selected_user['main_role']}")
st.write(f"**Jumlah Data Collect:** {selected_user['jumlah_collect']}")
st.write(f"**Jumlah Data Label:** {selected_user['jumlah_label']}")
st.write(f"**Total Aktivitas:** {selected_user['total_aktivitas']}")

# Opsional: tampilkan tabel semua user
st.subheader("Rekap")
st.dataframe(final_df[['email', 'name', 'main_role', 'jumlah_collect', 'jumlah_label', 'total_aktivitas']])


import altair as alt
import pandas as pd

# Pastikan kolom updated_at jadi datetime
df['updated_at'] = pd.to_datetime(df['updated_at'], format='ISO8601')

# Ambil tanggal saja (tanpa jam)
df['date'] = df['updated_at'].dt.date

# Filtering data untuk Collecting dan Labeling berdasarkan kondisi
collect_df = df[(df['is_collected'] == True) & (df['is_labeled'] == False)]
label_df = df[(df['is_collected'] == True) & (df['is_labeled'] == True)]

# Hitung jumlah collect per tanggal
collect_per_day = collect_df.groupby('date')['collection_user_id'].count().reset_index()
collect_per_day.columns = ['date', 'jumlah_collect']

# Hitung jumlah label per tanggal
label_per_day = label_df.groupby('date')['labeling_user_id'].count().reset_index()
label_per_day.columns = ['date', 'jumlah_label']

# Gabungkan
timeline_df = pd.merge(collect_per_day, label_per_day, on='date', how='outer').fillna(0)
timeline_df = timeline_df.sort_values(by='date')

# Bentuk long format untuk Altair
timeline_long = timeline_df.melt(id_vars='date', 
                                 value_vars=['jumlah_collect', 'jumlah_label'],
                                 var_name='aktivitas', 
                                 value_name='jumlah')

# Ganti label untuk chart
timeline_long['aktivitas'] = timeline_long['aktivitas'].replace({
    'jumlah_collect': 'Collecting',
    'jumlah_label': 'Labeling'
})

# Buat chart
chart = alt.Chart(timeline_long).mark_line(point=True).encode(
    x='date:T',
    y='jumlah:Q',
    color=alt.Color('aktivitas:N', scale=alt.Scale(domain=['Labeling', 'Collecting'],
                                                   range=['blue', 'gold'])),
    tooltip=['date:T', 'aktivitas:N', 'jumlah:Q']
).properties(
    title='Aktivitas Harian: Collecting vs Labeling',
    width=700,
    height=400
)

# Tampilkan di Streamlit
st.subheader("Rekap Harian Aktivitas")
st.altair_chart(chart, use_container_width=True)

