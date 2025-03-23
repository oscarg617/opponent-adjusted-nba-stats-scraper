'''Base endpoint class'''
class Endpoint:
    '''Stores and returns Dataframe or Dictionary'''
    data_frame = None
    data = None

    def get_data_frame(self):
        '''Returns data stored in a Pandas Dataframe'''
        return self.data_frame

    def get_dict(self):
        '''Returns data stored in a Dictionary'''
        return self.data

    def _format_year(self, year):
        start_year = year - 1
        end_year_format = year % 100
        if end_year_format >= 10:
            return f'{start_year}-{end_year_format}'
        return f'{start_year}-0{end_year_format}'
