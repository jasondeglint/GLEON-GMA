import datetime 

class db_info:
    def __init__(self, db_name, uploaded_by, institution):
        current_time = datetime.datetime.now()
        self.db_name = db_name
        self.uploaded_by = uploaded_by
        self.institution = institution
        self.upload_date = current_time
        self.db_id = db_name.replace(" ", "_") + '_' + uploaded_by.replace(" ", "_") + '_' + current_time.strftime("%Y%m%d_T%H%M%S_%f")