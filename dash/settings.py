"""
    Constant values utilized in Dash application
"""
import pandas as pd
import numpy as np

# Read in database info from the matadata file
metadataDB = pd.read_csv("data/MetadataDB.csv")

# Read in data from Pickle files into Pandas dataframes, and concatenate the data
alberta = pd.read_pickle("data/alberta.pkl")
florida = pd.read_pickle("data/florida.pkl")
df = pd.concat([alberta, florida], sort=False).reset_index(drop=True)

# Ratio of Total Nitrogen to Total Phosphorus
df["TN:TP"] = df["Total Nitrogen (ug/L)"]/df["Total Phosphorus (ug/L)"]

# Ration of Microcystin to Total Chlorophyll
df["Microcystin:Chlorophyll"] = df["Microcystin (ug/L)"]/df["Total Chlorophyll (ug/L)"]

# Percent change of microcystin
df["MC Percent Change"] = df.sort_values("DATETIME").\
                groupby(['LONG','LAT'])["Microcystin (ug/L)"].\
                apply(lambda x: x.pct_change()).fillna(0)

# Establish range of months and years that exist in data
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
year = pd.to_datetime(df['DATETIME']).dt.year
years = range(np.min(year), np.max(year)+1)

# Specify columns of interest
cols = ['Microcystin (ug/L)', 'Total Nitrogen (ug/L)', 'Total Phosphorus (ug/L)', 'Secchi Depth (m)', 'Total Chlorophyll (ug/L)', 'Temperature (degrees celsius)', 'Microcystin:Chlorophyll']

# Established microcystin limits
USEPA_LIMIT = 4
WHO_LIMIT = 20

# Identify all body of waters with more than 2 years of data
locations = []
locs = list(df["Body of Water Name"].unique())
locs.sort()
for l in locs:
    l_data = df[df["Body of Water Name"] == l]
    l_years = pd.to_datetime(l_data['DATETIME']).dt.year.unique()
    if len(l_years) > 2:
        locations.append(l)

