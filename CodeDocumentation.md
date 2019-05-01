## Dash App

**Video Demo:** For a demo of the current state of the application please refer to the posted gif on the project page. 

**"Upload New Data":** This section allows the users to upload their data in a formatted CSV or Excel file. The user will input their name, their institution, database name, and other optional information regarding the database. Once the file is uploaded and the "Done" button is pressed, the columns with entries will be saved as a "pkl" and a "csv" file. The file name is formatted based on the provided database name, user name, and the upload date. The uploaded database information is saved in "MetadataDB.csv". 
The required format of the uploaded database is in the "GLEON_GMA_Example.xlsx" file. In addition, the cells with invalid data (ex. "NA" or ".") must all be empty in the uploaded data as various strings create parsing issues in the backend. 

**Metadata Table:** The table contents are populated from the "MetadataDB.csv" file and allow the user to select a certain group of data to analyze. Once the user selects one or more databases from the table and the "Filter Data" button is pressed, all the graphs in the next section are populated. To separate each user’s selected data in the backend, the concatenated data of the selected databases is converted to a JSON string and stored in a hidden component in the layout. The stored string is then converted back to a dataframe to update all graphs.

**Graphs:** All graphs and the contents of their dropdowns are populated based on the converted JSON string in the hidden layout component. For trend graphs over a period of time, certain columns from the database including "Mean Depth", "Maximum Depth", and "MC Percent Change" are not shown. The code to populate the graphs and remove the specified column names from dropdown contents is in the "update_graph" callback function of "app.py".

## Code Files

### app.py
The file contains the main layout of the application in "app.layout"
-	"Upload New Data" section that allows the users to upload a CSV or an Excel 
-	The data table contents populated from the "MetadataDB.csv" file 
-	The graphs populated based on the filtered data, once the "Filter Data" button is pressed

The file also contains all "callback" functions that update different components based on user input and/or change in the UI component states. 

### data_analysis.py
The file contains all the functions that generate the graphs seen in the application. These functions are all called through the callbacks of app.py.
 
### db_engine.py
This file contains all the functions required to add database information in "MetadataDB.csv", parse database, save as "pkl" and "csv" files, as well as functions that return the user’s selected data for analyses.

### db_info.py
The class that contains database details, which makes it easier to handle all the inputs from "Upload New Data". 

### settings.py
This file contains the constants in the program including thresholds and months, as well as the initialization of the MetadataDB dataframe.

### assets – main.css
The code contains CSS classes for some components used in the app.

