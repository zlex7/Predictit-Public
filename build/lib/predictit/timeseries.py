class ContractInfoTimeSeries(object):
    def __init__(self, contract_info_series):
        # holds all data points for specific points in time, including trade price, volume (TODO), etc.
        self.contract_info_series = contract_info_series
        # self.VOLATILITY_PERCENTAGE_THRESHOLD = 0.1

    def get_percentage_change_from_start_to_end():
        return (end_info.last_trade_price - start_info.last_trade_price) / start_info.last_trade_price

    # def is_volatile_simple():
    #     start_info = self.contract_info_series[0]
    #     end_info = self.contract_info_series[-1];
    #     if (abs(end_info.last_trade_price - start_info.last_trade_price) > start_info.last_trade_price * self.VOLATILITY_PERCENTAGE_THRESHOLD)
    #         return True
    #     return False
