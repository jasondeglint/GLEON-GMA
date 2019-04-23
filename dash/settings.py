"""
    Constant values utilized in Dash application
"""
import pandas as pd
import numpy as np

# Read in database info from the matadata file
metadataDB = pd.read_csv("data/MetadataDB.csv")

# Establish range of months and years that exist in data
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Established microcystin limits
USEPA_LIMIT = 4
WHO_LIMIT = 20

