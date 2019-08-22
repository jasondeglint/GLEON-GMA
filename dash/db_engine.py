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

        # delete the extra composite section of the lake names - if they have any
        new_df['LakeName'] = new_df['LakeName'].\
            str.replace(r"[-]?.COMPOSITE(.*)", "", regex=True).\
            str.strip()
        
        new_df['Date'] = pd.to_datetime(new_df['Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
        print(new_df['LakeName'])
        # convert mg to ug
        new_df['TP_mgL'] *= 1000
        new_df['TN_mgL'] *= 1000

        # format all column names
        new_df.rename(columns={'Date': 'DATETIME',
                        'LakeName': 'Body of Water Name',
                        'Lat': 'LAT',
                        'Long': 'LONG',
                        'Altitude_m': 'Altitude (m)',
                        'MaximumDepth_m': 'Maximum Depth (m)',
                        'MeanDepth_m': 'Mean Depth (m)',
                        'SecchiDepth_m': 'Secchi Depth (m)',
                        'SamplingDepth_m': 'Sampling Depth (m)',
                        'ThermoclineDepth_m': 'Thermocline Depth (m)',
                        'SurfaceTemperature_C': 'Surface Temperature (degrees celsius)',
                        'EpilimneticTemperature_C': 'Epilimnetic Temperature (degrees celsius)',
                        'TP_mgL': 'Total Phosphorus (ug/L)',
                        'TN_mgL': 'Total Nitrogen (ug/L)',
                        'NO3NO2_mgL': 'NO3 NO2 (mg/L)',
                        'NH4_mgL': 'NH4 (mg/L)',
                        'PO4_ugL': 'PO4 (ug/L)',
                        'Chlorophylla_ugL': 'Total Chlorophyll a (ug/L)',
                        'Chlorophyllb_ugL': 'Total Chlorophyll b (ug/L)',
                        'Zeaxanthin_ugL': 'Zeaxanthin (ug/L)',
                        'Diadinoxanthin_ugL': 'Diadinoxanthin (ug/L)',
                        'Fucoxanthin_ugL': 'Fucoxanthin (ug/L)',
                        'Diatoxanthin_ugL': 'Diatoxanthin (ug/L)',
                        'Alloxanthin_ugL': 'Alloxanthin (ug/L)',
                        'Peridinin_ugL': 'Peridinin (ug/L)',
                        'Chlorophyllc2_ugL': 'Total Chlorophyll c2 (ug/L)',
                        'Echinenone_ugL': 'Echinenone (ug/L)',
                        'Lutein_ugL': 'Lutein (ug/L)',
                        'Violaxanthin_ugL': 'Violaxanthin (ug/L)',
                        'TotalMC_ug/L': 'Microcystin (ug/L)',
                        'DissolvedMC_ugL': 'DissolvedMC (ug/L)',
                        'MC_YR_ugL': 'Microcystin YR (ug/L)',
                        'MC_dmRR_ugL': 'Microcystin dmRR (ug/L)',
                        'MC_RR_ugL': 'Microcystin RR (ug/L)',
                        'MC_dmLR_ugL': 'Microcystin dmLR (ug/L)',
                        'MC_LR_ugL': 'Microcystin LR (ug/L)',
                        'MC_LY_ugL': 'Microcystin LY (ug/L)',
                        'MC_LW_ugL': 'Microcystin LW (ug/L)',
                        'MC_LF_ugL': 'Microcystin LF (ug/L)',
                        'NOD_ugL': 'Nodularin (ug/L)',
                        'CYN_ugL': 'Cytotoxin Cylindrospermopsin (ug/L)',
                        'ATX_ugL': 'Neurotoxin Anatoxin-a (ug/L)',
                        'GEO_ugL': 'Geosmin (ug/L)',
                        '2MIB_ngL': '2-MIB (ng/L)',
                        'TotalPhyto_CellsmL': 'Phytoplankton (Cells/mL)',
                        'Cyano_CellsmL': 'Cyanobacteria (Cells/mL)',
                        'PercentCyano': 'Relative Cyanobacterial Abundance (percent)',
                        'DominantBloomGenera': 'Dominant Bloom',
                        'mcyD_genemL': 'mcyD gene (gene/mL)',
                        'mcyE_genemL': 'mcyE gene (gene/mL)',},
                inplace=True)

        # remove NaN columns       
        new_df = new_df.dropna(axis=1, how='all')

        #save the pickle and csv file in the data directory
        pkldir = get_pkl_path(new_dbinfo.db_id)
        new_df.to_pickle(pkldir)

        csvdir = get_csv_path(new_dbinfo.db_id)
        new_df.to_csv(csvdir)

        # update the number of lakes and samples in db_info
        unique_lakes_list = list(new_df["Body of Water Name"].unique())
        new_dbinfo.db_num_lakes = len(unique_lakes_list)
        new_dbinfo.db_num_samples = new_df.shape[0]

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
        current_metadata = pd.read_csv("data/MetadataDB.csv")
        
        new_dbdf = pd.DataFrame({'DB_ID': [new_dbinfo.db_id],
                                'DB_name': [new_dbinfo.db_name],
                                'Uploaded_by': [new_dbinfo.uploaded_by],
                                'Upload_date': [new_dbinfo.upload_date],
                                'Published_url': [new_dbinfo.db_publication_url], #url
                                'Field_method_url': [new_dbinfo.db_field_method_url], #url
                                'Lab_method_url': [new_dbinfo.db_lab_method_url], #url
                                'QA_QC_url': [new_dbinfo.db_QAQC_url], #url
                                'Full_QA_QC_url': [new_dbinfo.db_full_QCQC_url], #url
                                'Substrate': [new_dbinfo.db_substrate],
                                'Sample_type': [new_dbinfo.db_sample_type],
                                'Field-method': [new_dbinfo.db_field_method],
                                'Microcystin_method': [new_dbinfo.db_microcystin_method],
                                'Filter_size': [new_dbinfo.db_filter_size],
                                'Cell_count_method': [new_dbinfo.db_cell_count_method],
                                'Ancillary_data': [new_dbinfo.db_ancillary_url],
                                'N_lakes': [new_dbinfo.db_num_lakes],
                                'N_samples': [new_dbinfo.db_num_samples]})

        metadataDB = pd.concat([current_metadata, new_dbdf], sort=False).reset_index(drop=True)
        metadataDB.to_csv("data/MetadataDB.csv", encoding='utf-8', index=False)
    except Exception as e:
        print(e)
        return 'Error saving metadata'

def update_dataframe(selected_rows):    
    """
        update dataframe based on selected databases 
    """
    try:
        new_dataframe = pd.DataFrame()    
        # Read in data from selected Pickle files into Pandas dataframes, and concatenate the data
        for row in selected_rows:
            rowid = row["DB_ID"]
            filepath = get_pkl_path(rowid)
            db_data = pd.read_pickle(filepath)
            new_dataframe = pd.concat([new_dataframe, db_data], sort=False).reset_index(drop=True)

        # Ratio of Total Nitrogen to Total Phosphorus
        # This line causes a problem on certain datasets as the columns are strings instead of ints and will not divide, dataset dependent
        print(new_dataframe["Total Nitrogen (ug/L)"])
        print("Phosphorus: ", new_dataframe["Total Phosphorus (ug/L)"])
        new_dataframe["TN:TP"] = new_dataframe["Total Nitrogen (ug/L)"]/new_dataframe["Total Phosphorus (ug/L)"]
        # Ration of Microcystin to Total Chlorophyll
        new_dataframe["Microcystin:Chlorophyll a"] = new_dataframe["Microcystin (ug/L)"]/new_dataframe["Total Chlorophyll a (ug/L)"]
        # Percent change of microcystin
        new_dataframe["MC Percent Change"] = new_dataframe.sort_values("DATETIME").\
                                            groupby(['LONG','LAT'])["Microcystin (ug/L)"].\
                                            apply(lambda x: x.pct_change()).fillna(0)
        return new_dataframe
    except Exception as e:
        print("EXCEPTION: ", e)

def get_pkl_path(db_id):
    return 'data/' + db_id + '.pkl'

def get_csv_path(db_id):
    return 'data/' + db_id + '.csv'
        