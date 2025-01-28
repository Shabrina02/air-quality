import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
st.title("Air Quality Dashboard - Guanyuan Station")
all_data = pd.read_csv("all_data.csv")
all_data['timestamp'] = pd.to_datetime(all_data['timestamp'])

# Ensure numeric columns
numeric_columns = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
for col in numeric_columns:
    all_data[col] = pd.to_numeric(all_data[col], errors='coerce')

# Sidebar for filtering
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input("Start Date", value=all_data['timestamp'].min().date())
end_date = st.sidebar.date_input("End Date", value=all_data['timestamp'].max().date())

# Filter data based on date picker
filtered_data = all_data[(all_data['timestamp'] >= pd.Timestamp(start_date)) & 
                         (all_data['timestamp'] <= pd.Timestamp(end_date))]

# Remove rows with NaN
filtered_data = filtered_data.dropna(subset=numeric_columns)

# Display filtered data
st.subheader("Filtered Data Table")
st.dataframe(filtered_data)


if filtered_data.empty:
    st.warning("No data available for the selected date range. Please adjust the date range.")
else:
    # Question 1
    st.subheader("Impact of Rainy Season on PM2.5 and PM10 Levels")
    rain_effect_data = filtered_data.groupby('RAIN').mean(numeric_only=True).reset_index()
    rain_effect_plot = px.scatter(rain_effect_data, x='RAIN', y=['PM2.5', 'PM10'],
                                  labels={'value': 'Pollution Level (µg/m³)', 'RAIN': 'Rainfall (mm)'},
                                  title="Impact of Rainfall on PM2.5 and PM10 Levels")
    st.plotly_chart(rain_effect_plot)
    

    # Question 2

    st.subheader("Monthly Average Rainfall")
    avg_rain = all_data.groupby("month")["RAIN"].mean().reset_index()
    fig3 = px.bar(avg_rain, x="month", y="RAIN", title="Monthly Average Rainfall", labels={"RAIN": "Curah Hujan (mm)"})
    st.plotly_chart(fig3)   

    temp_rain_data = filtered_data.groupby('TEMP').mean(numeric_only=True).reset_index()
    temp_rain_plot = px.scatter(temp_rain_data, x='TEMP', y='RAIN',
                                labels={'TEMP': 'Temperature (°C)', 'RAIN': 'Average Rainfall (mm)'},
                                title="Rainfall vs Temperature")
    st.plotly_chart(temp_rain_plot)

    # Question 3
    st.subheader("Main Cause of Pollution at Guanyuan Station")
    pollutant_corr = filtered_data[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'WSPM']].corr()
    main_pollutant = pollutant_corr[['PM2.5', 'PM10']].idxmax().values
    st.write(f"Based on the data, the primary contributors to PM2.5 and PM10 levels are:")
    st.write(f"- PM2.5: **{main_pollutant[0]}**")
    st.write(f"- PM10: **{main_pollutant[1]}**")

    pollutant_plot = px.scatter_matrix(filtered_data, dimensions=['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'WSPM'],
                                       title="Pollution Correlation Matrix")
    st.plotly_chart(pollutant_plot)

    # Advanced analysis
    st.subheader("Pollutant Levels in Guanyuan (WHO Guideline)")

    # Add column for pollution status based on WHO guidelines
    all_data['PM2.5_status'] = all_data['PM2.5'].apply(
        lambda x: 'Above WHO Standard' if x > 25 else 'Within WHO Standard'
    )
    all_data['PM10_status'] = all_data['PM10'].apply(
        lambda x: 'Above WHO Standard' if x > 50 else 'Within WHO Standard'
    )

    # Boxplot PM2.5
    st.markdown("### PM2.5 Levels Compared to WHO Standards")
    fig_pm25 = px.box(
    all_data,
    x='PM2.5_status',
    y='PM2.5',
    color='PM2.5_status',
    labels={'PM2.5': 'PM2.5 Level (µg/m³)', 'PM2.5_status': 'WHO Standard'},
    title="PM2.5 Levels Based on WHO Guidelines"
    )   
    st.plotly_chart(fig_pm25)

    # Boxplot PM10
    st.markdown("### PM10 Levels Compared to WHO Standards")
    fig_pm10 = px.box(
    all_data,
    x='PM10_status',
    y='PM10',
    color='PM10_status',
    labels={'PM10': 'PM10 Level (µg/m³)', 'PM10_status': 'WHO Standard'},
    title="PM10 Levels Based on WHO Guidelines"
    )
    st.plotly_chart(fig_pm10)

    # Summary
    st.markdown("### Summary of Pollution Levels")
    pollution_summary = pd.DataFrame({
    'Pollutant': ['PM2.5', 'PM10'],
    'Above WHO Standard (%)': [
        (all_data['PM2.5_status'] == 'Above WHO Standard').mean() * 100,
        (all_data['PM10_status'] == 'Above WHO Standard').mean() * 100
    ],
    'Within WHO Standard (%)': [
        (all_data['PM2.5_status'] == 'Within WHO Standard').mean() * 100,
        (all_data['PM10_status'] == 'Within WHO Standard').mean() * 100
    ]
    })
    st.table(pollution_summary)



