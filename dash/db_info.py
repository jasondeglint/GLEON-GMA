import datetime 

class db_info:
    def __init__(self, db_id, db_name, uploaded_by, institution):
        self.db_id = db_id
        self.db_name = db_name
        self.uploaded_by = uploaded_by
        self.institution = institution
        self.upload_date = datetime.datetime.now()