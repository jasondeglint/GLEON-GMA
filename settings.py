import pandas as pd
import numpy as np

alberta = pd.read_pickle("data/alberta.pkl")
florida = pd.read_pickle("data/florida.pkl")
df = pd.concat([alberta, florida], sort=False).reset_index(drop=True)

df["TN:TP"] = df["Total Nitrogen (ug/L)"]/df["Total Phosphorus (ug/L)"]

df["MC Percent Change"] = df.sort_values("DATETIME").\
                groupby(['LONG','LAT'])["Microcystin (ug/L)"].\
                apply(lambda x: x.pct_change()).fillna(0)

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
cols = ['Microcystin (ug/L)', 'Total Nitrogen (ug/L)', 'Total Phosphorus (ug/L)', 'Secchi Depth (m)', 'Total Chlorophyll (ug/L)', 'Temperature (degrees celsius)']
year = pd.to_datetime(df['DATETIME']).dt.year
years = range(np.min(year), np.max(year)+1)

USEPA_LIMIT = 4
WHO_LIMIT = 20

l = []
locations = list(df["Body of Water Name"].unique())
locations.sort()
for loc in locations:
    locs = df[df["Body of Water Name"] == loc]
    locs_years = pd.to_datetime(locs['DATETIME']).dt.year.unique()
    if len(locs_years) > 2:
        l.append(loc)

locations = l

