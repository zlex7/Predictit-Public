import numpy
from predictit.db import PredictItDb

class PredictIt():

    def __init__(self, time_intervals):
        self.time_intervals = [5,10,15,30]

    def get_standard_devs_for_all_markets(self):
        data = self.db.get_last_n_minutes_prices_for_all_markets()
        all_standard_devs = {}
        for market_id in data:
            if None not in data[market_id]:
                all_standard_devs[market_id] = self.calculate_standard_devs(data[market_id])
        return all_standard_devs

    def get_standard_devs_for_market(self,market_id):
        arr = [m.BestBuyYesCost for m in self.db.get_last_n_minutes_prices_for_market(market_id,minutes=self.time_intervals[-1])]
        return self.calculate_standard_devs(arr)

    def calculate_standard_devs(self,time_series):
        print(time_series)
        standard_devs = {}
        for time in self.time_intervals:
            standard_devs[time] = numpy.std(time_series[:time])
        return standard_devs

    def store_static_market_info(self,filename):
        self.db.store_static_csv(filename)

    def store_dynamic_market_info(self,filename):
        self.db.store_time_series_csv(filename)
