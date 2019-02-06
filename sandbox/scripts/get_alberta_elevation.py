import requests
import pandas as pd
import json

alberta = pd.read_pickle("../data/alberta.pkl")
alberta_elevation = alberta
alberta_elevation["Altitude"] = 0
seen_coords = {}
url = "http://geogratis.gc.ca/services/elevation/cdsm/altitude?lat=%s&lon=%s"

for index, row in alberta_elevation.iterrows():
    lat = row["LAT"]
    lon = row["LONG"]
    if (lat, lon) not in seen_coords.keys():
        url_params = url % (round(lat,1), round(lon,1)) 
        #print(url_params)
        response = requests.get(url_params)
        json_data = json.loads(response.text)
        alberta_elevation.loc[index, "Altitude"] = json_data["altitude"]
        #print(response.text)
        seen_coords[(lat,lon)] = json_data["altitude"]
    else:
        alberta_elevation.loc[index, "Altitude"] = seen_coords[(lat, lon)]
    
alberta_elevation.head()

# write to alberta pickle
alberta_elevation.to_pickle('../data/alberta.pkl')
