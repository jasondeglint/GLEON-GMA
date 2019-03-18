import base64
import datetime
import io
import pandas as pd
import numpy as np
from settings import metadataDB

def upload_new_database(new_dbinfo, contents, filename):
    """
        Decode contents of the upload component and create a new dataframe 
    """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            new_df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
            return parse_new_database(new_dbinfo, new_df)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            new_df = pd.read_excel(io.BytesIO(decoded))
            return parse_new_database(new_dbinfo, new_df)
        else:
            return 'Invalid file type.'
    except Exception as e:
        print(e)
        return 'There was an error processing this file.'

def parse_new_database(new_dbinfo, new_df):
    """
        Convert CSV or Excel file data into Pickle file and store in the data directory
    """    
    try:
        new_df["STN_NO_NM_LOC"] = new_df["STN_NO_NM_LOC"].\
            str.replace(r"[-]?.COMPOSITE(.*)", "", regex=True).\
            str.strip()
        
        new_df['DATETIME'] = pd.to_datetime(new_df['SAMPLE_DATETIME.1']).\
            dt.strftime('%Y-%m-%d %H:%M:%S')

        # convert mg to ug
        new_df["TP.mg.L"] *= 1000
        new_df["TN.mg.L"] *= 1000

        new_df.rename(columns={"M_LATITUDE": "LAT",
                        "LONGITUDE": "LONG",
                        "secchi.m": "Secchi Depth (m)",
                        "MC": "Microcystin (ug/L)",
                        "TP.mg.L": "Total Phosphorus (ug/L)",
                        "TN.mg.L": "Total Nitrogen (ug/L)",
                        "chla.ug.L": "Total Chlorophyll (ug/L)",
                        "Station Type": "Body of Water",
                        "1.0 m Water Temp DegC": "Temperature (degrees celsius)",
                        "STN_NO_NM_LOC": "Body of Water Name"},
                inplace=True)

        new_df = new_df[["LAT", "LONG", "Secchi Depth (m)", "Microcystin (ug/L)", "Total Phosphorus (ug/L)", "Total Nitrogen (ug/L)", "Total Chlorophyll (ug/L)", "Body of Water", "Temperature (degrees celsius)", "Body of Water Name", "DATETIME"]]

        #save the pickle file in the data directory
        pkldir = get_pkl_path(new_dbinfo.db_id)
        new_df.to_pickle(pkldir)
        current_metadata = metadataDB
        update_metadata(new_dbinfo, current_metadata)
        return u'''Database "{}" has been successfully uploaded.'''.format(new_dbinfo.db_name)
    
    except Exception as e:
        print(e)
        return 'Error uploading database'

def update_metadata(new_dbinfo, current_metadata):
    """
        Add new database info to MetadataDB.csv
    """ 
    try:
        new_dbdf = pd.DataFrame({'DB_ID': [new_dbinfo.db_id],
                                'DB_NAME': [new_dbinfo.db_name],
                                'UPLOADED_BY': [new_dbinfo.uploaded_by],
                                'UPLOAD_DATE': [new_dbinfo.upload_date]})
        metadataDB = pd.concat([current_metadata, new_dbdf], sort=False).reset_index(drop=True)
        metadataDB.to_csv("data/MetadataDB.csv", encoding='utf-8', index=False)
    except Exception as e:
        print(e)
        return 'Error saving metadata'

def get_pkl_path(db_id):
    return 'data/' + db_id + '.pkl'

#send in selected ids either as a list of DBInfo or just ids to update dataframe
def update_dataframe(selected_ids):    
    new_dataframe = pd.DataFrame() 
    
    # Read in data from selected Pickle files into Pandas dataframes, and concatenate the data
    for db_id in selected_ids:
        db_df = pd.read_pickle(db_id + '.pkl')
        new_dataframe = pd.concat([new_dataframe, db_df], sort=False).reset_index(drop=True)

    # Ratio of Total Nitrogen to Total Phosphorus
    new_dataframe["TN:TP"] = new_dataframe["Total Nitrogen (ug/L)"]/new_dataframe["Total Phosphorus (ug/L)"]

    # Ration of Microcystin to Total Chlorophyll
    new_dataframe["Microcystin:Chlorophyll"] = new_dataframe["Microcystin (ug/L)"]/new_dataframe["Total Chlorophyll (ug/L)"]

    # Percent change of microcystin
    new_dataframe["MC Percent Change"] = new_dataframe.sort_values("DATETIME").\
                    groupby(['LONG','LAT'])["Microcystin (ug/L)"].\
                    apply(lambda x: x.pct_change()).fillna(0)

    year = pd.to_datetime(new_dataframe['DATETIME']).dt.year
    years = range(np.min(year), np.max(year)+1)

    # Identify all body of waters with more than 2 years of data
    locations = []
    locs = list(new_dataframe["Body of Water Name"].unique())
    locs.sort()
    for l in locs:
        l_data = new_dataframe[new_dataframe["Body of Water Name"] == l]
        l_years = pd.to_datetime(l_data['DATETIME']).dt.year.unique()
        if len(l_years) > 2:
            locations.append(l)

    return new_dataframe
        