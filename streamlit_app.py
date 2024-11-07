import streamlit as st
import pandas as pd
from ucimlrepo import fetch_ucirepo
from datetime import datetime as dt

st.set_page_config(layout="wide")

# Get data
air_quality = fetch_ucirepo(id=360)
df = pd.DataFrame(air_quality.data.features)
molecules = ['CO(GT)', 'NO2(GT)', 'C6H6(GT)', 'NOx(GT)']

# Clean data
dateTime = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df.insert(0, 'DateTime', dateTime)
df['Date'] = pd.to_datetime(df['DateTime'], format='%Y-%m-%d %H-%M-%S')
df.sort_values('DateTime', inplace=True)
df = df[['DateTime', 'T', 'RH'] + molecules]
df.rename(columns={'CO(GT)': 'CO', 'NO2(GT)': 'NO2', 'C6H6(GT)': 'C6H6', 'NOx(GT)':'NOx'}, inplace=True)

# Get rid of columns missing values (will improve later...)
for col in df.columns:
    df = df[~df[col].isin([-200])]

# App
st.title("Italian Roadside Data Dashboard")
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

year_averageT = df['T'].mean()
year_maxT = df['T'].max()
year_lowT = df['T'].min()

year_averageH = df['RH'].mean()
year_maxH = df['RH'].max()
year_lowH = df['RH'].min()

filtered_df = df[(df['DateTime'] <= to_date) & (from_date <= df['DateTime'])]

maxT = filtered_df['T'].max()
lowT = filtered_df['T'].min()
averageT = filtered_df['T'].mean()
difference_maxT = maxT - year_maxT
difference_lowT = lowT - year_lowT
difference_avgT = averageT - year_averageT

maxH = filtered_df['RH'].max()
lowH = filtered_df['RH'].min()
averageH = filtered_df['RH'].mean()
difference_maxH = maxH - year_maxH
difference_lowH = lowH - year_lowH
difference_avgH = averageH - year_averageH

maxH = filtered_df['RH'].max()
differenceH = maxH - year_averageH

col1, col2, col3, col5, col6, col7 = st.columns(6)
with col1:
    st.metric('High', f'{maxT.round(2)} °C', f'{difference_maxT.round(2)} °C on year high')
with col2:
    st.metric('Avg ', f'{averageT.round(2)} °C', f'{difference_avgT.round(2)} °C on year avg')
with col3:
    st.metric('Low', f'{lowT.round(2)} °C', f'{difference_lowT.round(2)} °C on year low')
    
with col5:
    st.metric('High', f'{maxH.round(2)}%', f'{difference_maxT.round(2)}% on year high')
with col6:
    st.metric('Avg ', f'{averageH.round(2)}%', f'{difference_avgT.round(2)}% on year avg')
with col7:
    st.metric('Low', f'{lowH.round(2)}%', f'{difference_lowT.round(2)}% on year low')

st.divider()

# filtered_df = filtered_df[['DateTime', 'T', 'RH'] + selected_molecules]
filtered_df = filtered_df.groupby(filtered_df['DateTime'].dt.floor('D')).mean()

col1, col2 = st.columns(2)
with col1:
    st.line_chart(filtered_df, x='DateTime', y='T', y_label='Temperature (°C)', color='#2EA3D7', x_label='')
with col2:
    st.line_chart(filtered_df, x='DateTime', y='RH', y_label='% Relative Humidity', x_label='')

st.divider()

selected_molecules = st.multiselect(
    "Which metal oxide concentrations would you like to measure?",
    ['CO', 'NO2', 'C6H6', 'NOx'],
    ['CO', 'NO2', 'C6H6', 'NOx']
    )

st.divider()

units = {'CO': 'mg m⁻³', 'C6H6': 'ug m⁻³', 'NO2': 'ug m⁻³', 'NOx': 'ppb'}
colors = {'CO': '#b276b2', 'C6H6': '#faa43a', 'NO2': '#60bd68', 'NOx': '#f15854'}

for molecule in selected_molecules:
    st.line_chart(filtered_df,
                  x='DateTime',
                  y=molecule,
                  x_label='',
                  y_label=(molecule + ' Concentration  ' + f'({units[molecule]})'),
                  color=colors[molecule]
                  )
