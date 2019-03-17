"""
    Constant values utilized in Dash application
"""
import pandas as pd
import numpy as np

# Read in database info from the matadata file
metadataDB = pd.read_csv("data/MetadataDB.csv")

# only load 0001 file at first 
initial_df = pd.read_pickle("data/0001.pkl")

# Ratio of Total Nitrogen to Total Phosphorus
initial_df["TN:TP"] = initial_df["Total Nitrogen (ug/L)"]/initial_df["Total Phosphorus (ug/L)"]

# Ration of Microcystin to Total Chlorophyll
initial_df["Microcystin:Chlorophyll"] = initial_df["Microcystin (ug/L)"]/initial_df["Total Chlorophyll (ug/L)"]

# Percent change of microcystin
initial_df["MC Percent Change"] = initial_df.sort_values("DATETIME").\
                                groupby(['LONG','LAT'])["Microcystin (ug/L)"].\
                                apply(lambda x: x.pct_change()).fillna(0)

# Establish range of months and years that exist in data
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
year = pd.to_datetime(initial_df['DATETIME']).dt.year
years = range(np.min(year), np.max(year)+1)

# Specify columns of interest
cols = ['Microcystin (ug/L)', 'Total Nitrogen (ug/L)', 'Total Phosphorus (ug/L)', 'Secchi Depth (m)', 'Total Chlorophyll (ug/L)', 'Temperature (degrees celsius)', 'Microcystin:Chlorophyll']

# Established microcystin limits
USEPA_LIMIT = 4
WHO_LIMIT = 20

# Identify all body of waters with more than 2 years of data
locations = []
locs = list(initial_df["Body of Water Name"].unique())
locs.sort()
for l in locs:
    l_data = initial_df[initial_df["Body of Water Name"] == l]
    l_years = pd.to_datetime(l_data['DATETIME']).dt.year.unique()
    if len(l_years) > 2:
        locations.append(l)

