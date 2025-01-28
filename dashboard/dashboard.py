import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
st.title("Air Quality Dashboard - Guanyuan Station")
all_data = pd.read_csv("https://github.com/Shabrina02/air-quality/blob/main/dashboard/all_data.csv")
all_data['timestamp'] = pd.to_datetime(all_data['timestamp'])

sorted_months = list(range(1, 13))  # Proper month order

# Sidebar for user interaction
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Year", sorted(all_data['year'].unique()))
selected_month = st.sidebar.selectbox("Month", sorted_months)
selected_day = st.sidebar.selectbox("Day", sorted(all_data['day'].unique()))

# Sidebar for user interaction
#st.sidebar.header("Filter Data")
#selected_year = st.sidebar.selectbox("Year", all_data['year'].unique())
#selected_month = st.sidebar.selectbox("Month", all_data['month'].unique())
#selected_day = st.sidebar.selectbox("Day", all_data['day'].unique())


# Filter data based on sidebar inputs
filtered_data = all_data[(all_data['year'] == selected_year) &
                         (all_data['month'] == selected_month) &
                         (all_data['day'] == selected_day)]

# Display the filtered data
st.subheader("Data Table")
st.dataframe(filtered_data.style.format({"year": "{:.0f}"}))  # Menampilkan tahun tanpa koma

# Visualize PM2.5 and PM10 trends
st.subheader("PM2.5 and PM10 Trends")
if not filtered_data.empty:
    fig_pm = px.line(filtered_data, x='timestamp', y=['PM2.5', 'PM10'],
                     labels={'value': 'Concentration (µg/m³)', 'variable': 'Pollutant'},
                     title="PM2.5 and PM10 Levels Over Time")
    fig_pm.update_layout(xaxis_title="Time", yaxis_title="Pollutant Level (µg/m³)")
    st.plotly_chart(fig_pm)
else:
    st.write("No data available for the selected filters.")

# Visualize Monthly Average Rainfall
st.subheader("Monthly Average Rainfall")
avg_rain = all_data.groupby("month")["RAIN"].mean().reset_index()
fig3 = px.bar(avg_rain, x="month", y="RAIN", title="Monthly Average Rainfall", labels={"RAIN": "Curah Hujan (mm)"})
st.plotly_chart(fig3)

# Geospatial Rainfall Scatter Map
rainfall_data = all_data.copy()
rainfall_data['latitude'] = 39.9306
rainfall_data['longitude'] = 116.3287

# Scatter map for rainfall
fig_scatter = px.scatter_mapbox(
    rainfall_data,
    lat='latitude',
    lon='longitude',
    color='RAIN',
    size='RAIN',
    size_max=15,
    zoom=10,
    mapbox_style="open-street-map",
    title="Scatter Map of Rainfall Over Time",
    animation_frame='month',
    labels={'RAIN': 'Rainfall (mm)', 'month': 'Month'}
)

st.plotly_chart(fig_scatter)

# Visualize Monthly Average Rainfall
st.subheader("WHO Guidelines for Particulate Matter")
who_pm25 = 15  # Batas WHO PM2.5 dalam µg/m3
who_pm10 = 45  # Batas WHO PM10 dalam µg/m3
st.write(f"daily avg limit for PM2.5 is 15 µg/m³")
st.write(f"daily avg limit for PM10 is  45 µg/m³")
exceed_pm25 = filtered_data[filtered_data['PM2.5'] > who_pm25]
exceed_pm10 = filtered_data[filtered_data['PM10'] > who_pm10]
st.write(f"number of samples exceeds the WHO's safe limit")
st.write(f"PM2.5: {len(exceed_pm25)} samples")
st.write(f"PM10: {len(exceed_pm10)} samples")
