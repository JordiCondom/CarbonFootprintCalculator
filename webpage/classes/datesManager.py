from datetime import datetime, timedelta

class DatesManager:
    def __init__(self, date_range_type, start_date, end_date):
        self.date_range_type = date_range_type
        self.start_date = None
        self.end_date = None
        self.number_of_days = 0

        self.set_start_end_date(start_date, end_date)

    def set_start_end_date(self, start_date, end_date):
        if self.date_range_type == "range-dates":
            self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        elif self.date_range_type == "last-week":
            self.end_date = datetime.now().date()
            self.start_date = self.end_date - timedelta(days=7)
        elif self.date_range_type == "last-month":
            self.end_date = datetime.now().date()
            self.start_date = self.end_date - timedelta(days=30)
        elif self.date_range_type == "last-year":
            self.end_date = datetime.now().date()
            self.start_date = self.end_date - timedelta(days=365)

        self.calculate_number_of_days()

    def calculate_number_of_days(self):
        if self.start_date and self.end_date:
            self.number_of_days = (self.end_date - self.start_date).days
        else:
            self.number_of_days = 0

    def get_start_date(self):
        return self.start_date
    
    def get_end_date(self):
        return self.end_date
    
    def get_number_of_days(self):
        return self.number_of_days
