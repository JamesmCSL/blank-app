import streamlit as st
import pandas as pd
from ucimlrepo import fetch_ucirepo
from streamlit_pandas_profiling import st_profile_report
from datetime import datetime as dt

# Get data

air_quality = fetch_ucirepo(id=360)
df = pd.DataFrame(air_quality.data.features)

# Clean data
dateTime = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df.insert(0, 'DateTime', dateTime)
df['Date'] = pd.to_datetime(df['DateTime'])
df['Date'] = pd.to_datetime(df['Time'])
df.sort_values('DateTime', inplace=True)

# Get rid of columns missing values (will improve later...)
df = df[~df['T'].isin([-200])]
df = df[~df['CO(GT)'].isin([-200])]
df = df[~df['NO2(GT)'].isin([-200])]
df = df[~df['RH'].isin([-200])]

# Data Selection
temps = df.groupby(df['Date'].dt.floor('D'))['T'].mean()
humidity = df.groupby(df['Date'].dt.floor('D'))['RH'].mean()

# App
st.title("CloudSecure Ltd Data Dashboard")
st.divider()
st.write(
    "Welcome to the dashboard. Let's look at some Italian town data from 2004!"
)
st.divider()

date_min = dt.strptime(df.DateTime.min().strftime('%Y-%m-%d'), '%Y-%m-%d')
date_max = dt.strptime(df.DateTime.max().strftime('%Y-%m-%d'), '%Y-%m-%d')

from_date, to_date = st.slider(
    min_value = date_min,
    max_value = date_max,
    value = [date_min, date_max],
    label='Please select a date range:'
    )

st.divider()

filtered_df = df[(df.DateTime <= to_date) & (df.DateTime >= from_date)]

temps = filtered_df.groupby(df['DateTime'].dt.floor('D'))['T'].mean()
humidity = filtered_df.groupby(df['DateTime'].dt.floor('D'))['RH'].mean()

st.line_chart(temps, x_label='Date', y_label='Temperature (°C)', color='#2EA3D7')
st.line_chart(humidity, x_label='Date', y_label='% Relative Humidity')
