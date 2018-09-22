#!/usr/bin/python3

import pandas as pd
import numpy as np

# Script to import Florida data into pandas DataFrame, format headers, and save as a pickle file

florida = '../data/Stephens MC_FLLakewatchWQ_Data.xlsx'
df = pd.read_excel(florida)

df = df.rename(columns=lambda x: x.strip())
df['Lake'] = df['Lake'].str.strip()
df = df.replace('\.+', np.nan, regex=True)

df['Temperature (degrees celsius)'] = np.nan
df['Body of Water'] = 'Lake'

df.rename(columns={'Latitude': 'LAT', 'Longitude': 'LONG', 'Secchi (m)': 'Secchi Depth (m)', 'Microcystin concentration (µg/L)': 'Microcystin (ug/L)', 'Total phosphorus (µg/L)': 'Total Phosphorus (ug/L)', 'Total nitrogen (µg/L)': 'Total Nitrogen (ug/L)', 'Total chlorophyll (µg/L)': 'Total Chlorophyll (ug/L)', 'Lake': 'Body of Water Name'}, inplace=True)

df['DATETIME'] = pd.to_datetime(df[['Year', 'Month', 'Day']])

df.drop(['County', 'Year', 'Month', 'Day'], axis=1, inplace=True)

#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows',900)
#print(df)

df.to_pickle('../data/florida.pkl')