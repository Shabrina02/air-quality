import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load dataset
st.title("Air Quality Dashboard - Guanyuan Station")
all_data = pd.read_csv("https://raw.githubusercontent.com/Shabrina02/air-quality/refs/heads/main/dashboard/all_data.csv")
all_data['timestamp'] = pd.to_datetime(all_data['timestamp'])

# Memastikan kolom numerik
numeric_columns = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
for col in numeric_columns:
    all_data[col] = pd.to_numeric(all_data[col], errors='coerce')

# Tentukan rentang tanggal minimum dan maksimum
min_date = pd.to_datetime(all_data['timestamp']).min()
max_date = pd.to_datetime(all_data['timestamp']).max()

# Buat sidebar di sebelah kiri
with st.sidebar:
  st.image("https://www.deq.ok.gov/wp-content/uploads/air-division/aqi_mini-1200x675.png", width=500)
  # Sidebar time
  start_date = st.date_input("Tanggal Mulai", value=min_date, min_value=min_date, max_value=max_date)
  end_date = st.date_input("Tanggal Akhir", value=max_date, min_value=min_date, max_value=max_date)

  # Validasi input pengguna
  if start_date > end_date:
      st.error("Tanggal mulai harus lebih kecil dari tanggal akhir.")
      start_date = min_date
      end_date = max_date

# Filter data
filtered_data = all_data[(all_data['timestamp'] >= pd.Timestamp(start_date)) &
                         (all_data['timestamp'] <= pd.Timestamp(end_date))]


# Hapus baris NaN
filtered_data = filtered_data.dropna(subset=numeric_columns)

if filtered_data.empty:
    st.warning("No data available for the selected date range. Please adjust the date range.")
else:
    # Pertanyaan 1
    st.subheader("Dampak Hujan terhadap Polusi Udara")
    filtered_data['RAIN'] = pd.to_numeric(filtered_data['RAIN'], errors='coerce')
    filtered_data['PM2.5'] = pd.to_numeric(filtered_data['PM2.5'], errors='coerce')
    filtered_data['PM10'] = pd.to_numeric(filtered_data['PM10'], errors='coerce')
    filtered_data['rain_category'] = filtered_data['RAIN'].apply(lambda x: 'Hujan' if x > 0 else 'Tidak Hujan')

    # Hitung mean tiap kategori polutan
    mean_pollution = filtered_data.groupby('rain_category')[['PM2.5', 'PM10']].mean()

    # Visualisasi boxplot
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    sns.boxplot(x='rain_category', y='PM2.5', data=filtered_data, ax=axes[0])
    axes[0].set_title('PM2.5 Level Saat Hujan vs Tidak Hujan')
    sns.boxplot(x='rain_category', y='PM10', data=filtered_data, ax=axes[1])
    axes[1].set_title('PM10 Level Saat Hujan vs Tidak Hujan')
    st.pyplot(fig)

    # Visualisasi scatter plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=filtered_data, x='RAIN', y='PM2.5', alpha=0.5)
    plt.title('Hubungan antara Curah Hujan dan PM2.5')
    plt.xlabel('Curah Hujan (mm)')
    plt.ylabel('PM2.5 (µg/m³)')
    plt.grid()
    st.pyplot(plt)


    # Uji t-test
    ttest_pm25 = stats.ttest_ind(
        filtered_data[filtered_data['rain_category'] == 'Hujan']['PM2.5'].dropna(),
        filtered_data[filtered_data['rain_category'] == 'Tidak Hujan']['PM2.5'].dropna()
    )

    ttest_pm10 = stats.ttest_ind(
        filtered_data[filtered_data['rain_category'] == 'Hujan']['PM10'].dropna(),
        filtered_data[filtered_data['rain_category'] == 'Tidak Hujan']['PM10'].dropna()
    )

    # Tampilkan hasil perhitungan mean pollution
    st.write("Rata-rata Tingkat Polusi berdasarkan Kategori Hujan (T-test):")
    st.dataframe(mean_pollution)
   

    # Pertanyaan 2
    st.subheader("Hubungan Curah Hujan dan Suhu")
    # Visualisasi scatter plot - Suhu vs Curah Hujan
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=filtered_data, x='TEMP', y='RAIN', alpha=0.7, color='blue')
    plt.title('Hubungan Curah Hujan dan Suhu', fontsize=16)
    plt.xlabel('Suhu (°C)', fontsize=14)
    plt.ylabel('Curah Hujan (mm)', fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(plt)

    # Pertanyaan 3
    st.subheader("Penyebab Utama Polusi")
    correlation_columns = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']

    # Hitung korelasi
    correlation_data = all_data[correlation_columns].corr()

    # Plot heatmap menggunakan Plotly dengan skema warna yang disesuaikan
    fig_correlation = px.imshow(
    correlation_data,
    labels=dict(color="Correlation"),
    x=correlation_columns,
    y=correlation_columns,
    color_continuous_scale="RdBu_r", 
    title="Heatmap Korelasi: Polutan dan Parameter Cuaca"
    )
    # Tampilkan heatmap di Streamlit
    st.plotly_chart(fig_correlation)

    # Preproses data (konversi tipe data numerik dan kategorisasi hujan)
    filtered_data['SO2'] = pd.to_numeric(filtered_data['SO2'], errors='coerce')
    filtered_data['NO2'] = pd.to_numeric(filtered_data['NO2'], errors='coerce')
    filtered_data['CO'] = pd.to_numeric(filtered_data['CO'], errors='coerce')
    filtered_data['O3'] = pd.to_numeric(filtered_data['O3'], errors='coerce')

    # Hitung rata-rata polusi per bulan
    monthly_pollution = filtered_data.groupby('month')[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean()

    # Visualisasi rata-rata polusi per bulan
    plt.figure(figsize=(12, 6))
    monthly_pollution.plot(kind='line', marker='o')
    plt.title('Rata-rata Polutan Berdasarkan Bulan')
    plt.xlabel('Bulan')
    plt.ylabel('Konsentrasi Polutan (µg/m³)')
    plt.grid()
    st.pyplot(plt)

    # Hitung rata-rata polusi per jam
    hourly_pollution = filtered_data.groupby('hour')[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean()

    # Visualisasi rata-rata polusi per jam
    plt.figure(figsize=(12, 6))
    hourly_pollution.plot(kind='line', marker='o')
    plt.title('Rata-rata Polutan Berdasarkan Jam dalam Sehari')
    plt.xlabel('Jam')
    plt.ylabel('Konsentrasi Polutan (µg/m³)')
    plt.grid()
    st.pyplot(plt)

    #Analisis Lanjutan
    # Preproses data (konversi tipe data numerik)
    filtered_data_copy = filtered_data.copy()  # Gunakan copy untuk menghindari perubahan pada data asli
    # Tambahkan kolom datetime
    filtered_data_copy['datetime'] = pd.to_datetime(filtered_data_copy[['year', 'month', 'day', 'hour']])

    # Hitung rata-rata harian PM2.5 dan PM10
    daily_avg = filtered_data_copy.groupby(['year', 'month', 'day'], as_index=False).agg({
      'PM2.5': 'mean',
      'PM10': 'mean'
  })
    daily_avg['date'] = pd.to_datetime(daily_avg[['year', 'month', 'day']])

  # Tetapkan batas WHO
    who_limits = {
      'PM2.5': 15,  # µg/m³ (24 jam)
      'PM10': 45   # µg/m³ (24 jam)
  }

    # Cek apakah melebihi batas WHO
    daily_avg['PM2.5_Exceeds_WHO'] = daily_avg['PM2.5'] > who_limits['PM2.5']
    daily_avg['PM10_Exceeds_WHO'] = daily_avg['PM10'] > who_limits['PM10']

    # Boxplot distribusi harian PM2.5 dan PM10
    st.subheader("Analisis Lanjutan: Pedoman WHO untuk Batas Aman Polutan")
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=daily_avg[['PM2.5', 'PM10']])
    plt.axhline(y=who_limits['PM2.5'], color='red', linestyle='--', label='WHO PM2.5 Limit (15 µg/m³)')
    plt.axhline(y=who_limits['PM10'], color='blue', linestyle='--', label='WHO PM10 Limit (45 µg/m³)')
    plt.title('Distribusi Harian PM2.5 dan PM10 di Guanyuan')
    plt.ylabel('Level (µg/m³)')
    plt.legend()
    st.pyplot(plt)

    # Heatmap hari melebihi batas WHO (PM2.5)
    daily_avg_heatmap = all_data.groupby(['year', 'month', 'day'], as_index=False).agg({
    'PM2.5': 'mean',
    'PM10': 'mean' })
    daily_avg_heatmap['date'] = pd.to_datetime(daily_avg_heatmap[['year', 'month', 'day']])
    daily_avg_heatmap['PM2.5_Exceeds_WHO'] = daily_avg_heatmap['PM2.5'] > who_limits['PM2.5']
    heatmap_data_pivot = daily_avg_heatmap.pivot_table(values='PM2.5_Exceeds_WHO', index='month', columns='day', aggfunc='sum')
    plt.figure(figsize=(14, 8))
    sns.heatmap(heatmap_data_pivot, cmap='Reds', cbar_kws={'label': 'PM2.5 Exceeds WHO Limit (Days)'})
    plt.title('Hari dengan PM2.5 Melebihi Batas WHO di Setiap Bulan')
    plt.xlabel('Hari dalam Sebulan')
    plt.ylabel('Bulan')
    st.pyplot(plt)

    # Heatmap hari melebihi batas WHO (PM10)
    daily_avg_heatmap['date'] = pd.to_datetime(daily_avg_heatmap[['year', 'month', 'day']])
    daily_avg_heatmap['PM10_Exceeds_WHO'] = daily_avg_heatmap['PM10'] > who_limits['PM2.5']
    heatmap_data_pivot = daily_avg_heatmap.pivot_table(values='PM10_Exceeds_WHO', index='month', columns='day', aggfunc='sum')
    plt.figure(figsize=(14, 8))
    sns.heatmap(heatmap_data_pivot, cmap='Blues', cbar_kws={'label': 'PM10 Exceeds WHO Limit (Days)'})
    plt.title('Hari dengan PM10 Melebihi Batas WHO di Setiap Bulan')
    plt.xlabel('Hari dalam Sebulan')
    plt.ylabel('Bulan')
    st.pyplot(plt)

    # Line chart tren tahunan PM2.5 dan PM10
    annual_avg = filtered_data_copy.groupby('year', as_index=False).agg({
      'PM2.5': 'mean',
      'PM10': 'mean'
  })

    plt.figure(figsize=(10, 6))
    plt.plot(annual_avg['year'], annual_avg['PM2.5'], marker='o', label='PM2.5')
    plt.plot(annual_avg['year'], annual_avg['PM10'], marker='o', label='PM10')
    plt.axhline(y=who_limits['PM2.5'], color='red', linestyle='--', label='WHO PM2.5 Limit (Annual 5 µg/m³)')
    plt.axhline(y=who_limits['PM10'], color='blue', linestyle='--', label='WHO PM10 Limit (Annual 15 µg/m³)')
    plt.title('Tren Tahunan PM2.5 dan PM10 di Guanyuan')
    plt.xlabel('Year')
    plt.ylabel('Level (µg/m³)')
    plt.legend()
    st.pyplot(plt)

  # Hitung jumlah hari melebihi batas WHO
    pm25_exceeds = daily_avg['PM2.5_Exceeds_WHO'].sum()
    pm10_exceeds = daily_avg['PM10_Exceeds_WHO'].sum()
    st.write(f"Jumlah hari PM2.5 melebihi batas WHO: {pm25_exceeds}")
    st.write(f"Jumlah hari PM10 melebihi batas WHO: {pm10_exceeds}")
