import datetime 

class db_info:
    def __init__(self, db_name, uploaded_by, institution):
        current_date = datetime.datetime.now()
        self.db_name = db_name
        self.uploaded_by = uploaded_by
        self.institution = institution
        self.upload_date = current_date.strftime("%Y\%m\%d")
        self.db_id = db_name.replace(" ", "_") + '_' + uploaded_by.replace(" ", "_") + '_' + current_date.strftime("%Y\%m\%d")
        
        self.db_publication_url = ''
        self.db_field_method_url = ''
        self.db_lab_method_url = ''
        self.db_QAQC_url = ''
        self.db_full_QCQC_url = ''
        self.db_substrate = ''
        self.db_sample_type = ''
        self.db_field_method = ''
        self.db_cyano_method = ''
        self.db_filter_size = ''
        self.db_cell_count_method = ''
        self.db_ancillary_url = ''
        self.db_num_lakes = 0
        self.db_num_samples = 0