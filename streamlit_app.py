import streamlit as st
import pandas as pd
from ucimlrepo import fetch_ucirepo
from datetime import datetime as dt

st.set_page_config(layout="wide")

# Get data
air_quality = fetch_ucirepo(id=360)
df = pd.DataFrame(air_quality.data.features)
gases = ['CO(GT)', 'NO2(GT)', 'C6H6(GT)', 'NOx(GT)']

# Clean data
dateTime = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df.insert(0, 'DateTime', dateTime)
df['Date'] = pd.to_datetime(df['DateTime'], format='%Y-%m-%d %H-%M-%S')
df.sort_values('DateTime', inplace=True)
df = df[['DateTime', 'T', 'RH'] + gases]
df.rename(columns={'CO(GT)': 'CO', 'NO2(GT)': 'NO2', 'C6H6(GT)': 'C6H6', 'NOx(GT)':'NOx'})

# Get rid of columns missing values (will improve later...)
for col in df.columns:
    df = df[~df[col].isin([-200])]

# App
st.title("Italian Roadside Data Dashboard")
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

selected_gases = st.multiselect(
    "Which metal oxide concentrations would you like to measure?",
    ['CO', 'NO2', 'C6H6', 'NOx'],
    ['CO', 'NO2', 'C6H6', 'NOx']
)

st.divider()

filtered_df = df[(df.DateTime <= to_date) & (df.DateTime >= from_date)]
filtered_df = df[['DateTime', 'T', 'RH']]

# df_gases = df[[selected_gases].append('DateTime')]

# st.write(f"{selected_gases}")

temps = filtered_df.groupby(df['DateTime'].dt.floor('D'))['T'].mean()
humidity = filtered_df.groupby(df['DateTime'].dt.floor('D'))['RH'].mean()

col1, col2 = st.columns(2)
with col1:
    st.line_chart(temps, y_label='Temperature (°C)', color='#2EA3D7')
with col2:
    st.line_chart(humidity, y_label='% Relative Humidity')
