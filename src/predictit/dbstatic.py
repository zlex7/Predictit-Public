## This API should:

# 1. Get averages of values for each hour of past 24 hoursself.
# 2. Get last n 5 second interval values.
# 3. Put a 5 second interval into the database using the contractInfo class
import redis
import traceback
import time
import logging
from predictit.models import *

logger = logging.getLogger('predictit-db')

class PredictItDb(object):

    def __init__(self, db_host, db_port):
        pass

    def put_market_volume(self, market_volume_data):
        '''
            save market volume data for timestamp
        '''
        pass

    def put_contract_order_book(self, contract_order_book):
        '''
            save contract order book data for timestamp
        '''
        pass

class TimeIndexedFile(object):

    def __init__(self, f, time):
        pass

class FilePredictItDb(PredictItDb):

    def __init__(self, db_host=None, db_port=None):
        # maps ticker symbols to files
        self.contract_ticker_symbol_to_files = {}

    def put_market_volume(self, market_volume_data):
        if market_volume_data.ticker_symbol not in self.contract_ticker_symbol_to_files:
            self.contract_ticker_symbol_to_files = open()

    def put_contract_order_book(self, contract_order_book):
        if ('%s | %sh' % (contract_order_book.ticker_symbol,contract_order_book.hour)) not in self.contract_ticker_symbol_to_files:
            
        pass

# class PredictItDb(object):
#
#     def __init__(self, db_host, db_port):
#         pass
#
#     def put_market(self, market):
#         self.put_all_markets([market])
#
#     def put_all_markets(self, market_list):
#         pass
#
#     def get_market(self, ticker_symbol):
#         self.get_markets([ticker_symbol])
#
#     def get_markets(self, symbols_to_get):
#         pass
#
#     def get_all_markets(self):
#         pass
#
#     def delete_markets(self, ticker_symbol_list):
#         pass
#
#     def put_contract(self, contract):
#         self.put_all_contracts([contract])
#
#     def put_all_contracts(self, contracts):
#         pass
#
#     def get_contract(self, ticker_symbol):
#         self.get_contracts([ticker_symbol])
#
#     def get_contracts(self, contract_ticker_symbols):
#         pass
#
#     def get_all_contracts(self):
#         pass
#
#     def delete_contract(self, ticker_symbol):
#         self.delete_contracts([ticker_symbol])
#
#     def delete_contracts(self, symbols_to_delete):
#         pass
#
#     def delete_all_contracts(self):
#         pass
#
#     def put_contract_info(self, contract_ticker_symbol, contract_info):
#         pass
#
#     def put_multiple_contracts_info(self, contract_ticker_symbol, contract_info_points):
#         pass
#
#     def get_contract_info(self, contract_ticker_symbol, hours=0, minutes=15, seconds=0, start_time=None):
#         pass
#
#     def get_all_contracts_info(self, hours=0, minutes=15, seconds=0, start_time=None):
#         pass
