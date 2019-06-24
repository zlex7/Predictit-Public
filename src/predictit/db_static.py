## This API should:

# 1. Get averages of values for each hour of past 24 hoursself.
# 2. Get last n 5 second interval values.
# 3. Put a 5 second interval into the database using the contractInfo class
import redis
import traceback
import time
import logging
from predictit.models import *
import csv
import os
import datetime

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

    def __init__(self, target=None, unique_id=None, 
    	start=None, end=None, agent_account=None, db_host=None, db_port=None):

        # Do some string parsing
        self.target = target
        self.unique_id = unique_id
        self.start = start.replace(" ", "").replace(".", "").replace("/", "_")
        self.end = end.replace(" ", "").replace(".", "").replace("/", "_")
        self.agent_account = agent_account[:agent_account.index("@")] 

       # Create_unique_identifier_string for file writing
        self.file_str = self.target+"_uniqueid"+str(self.unique_id)+"_start"+self.start+"_end"+self.end+"_agent"+self.agent_account
        # maps ticker symbols to files
        self.contract_ticker_symbol_to_files = {}

        # Create path to data
        if not os.path.exists('./data/%s' % self.target):
            os.makedirs('./data/%s' % self.target)

    def put_market_volume(self, market_volume_data):
        """
        Writes the market volume for each hour into a CSV. 

        We are going to scrape every 15 minutes because we're not sure exactly how often they update the 
        volume data in order to obtain the highest fidelity data possible. 

        This one just writes 1 file because they aren't that many rows we have to write. 

        :market_volume_data: MarketVolumeData object
        
        :ret: None
        """

        file_key = self.file_str+"_VOLUME"
        if file_key not in self.contract_ticker_symbol_to_files:
             # Create new folder
            if not os.path.exists('./data/%s/%s/' % (self.target, file_key)):
                os.makedirs('./data/%s/%s/' % (self.target, file_key))
            
            self.contract_ticker_symbol_to_files[file_key] = open('./data/%s/%s/%s.csv' % (self.target, file_key, file_key), 'w')
            
            # Create the writer
            write_file = self.contract_ticker_symbol_to_files[file_key]
            writer = csv.writer(write_file, delimiter=',')
            writer.writerow(["ticker_symbol", "timestamp", "volume"])
        else:
            write_file = self.contract_ticker_symbol_to_files[file_key]
            writer = csv.writer(write_file, delimiter=',')

        logging.info('Writing row for contract %s' % file_key)

        # Write the row
        writer.writerow([market_volume_data.ticker_symbol, market_volume_data.timestamp, ", ".join(str(x) for x in market_volume_data.contract_volumes)])
        write_file.flush()

    def put_contract_order_book(self, contract_order_book):
        """
        This method takes in a ContractOrderBook object and writes it to a csv file. 

        We are currently creating a new file to write to every 1 hour to preserve 
        the integrity of data in case of failures. It also reduces memory concerns. 

        An example of the resulting file structure looks like: 

        data
        ----vp
        --------yymmddhh1
        ------------order_book_csv file1
        ------------volume_data_csv file1
        --------yymmddhh2
        ------------order_book_csv_file2
        ----potus
        --------yymmddhh1
        ------------order_book_csv file1
        ------------volume_data_csv file1
        --------yymmddhh2
        ------------order_book_csv_file2
        ----rdt
        
        In general:

        /data
            /target_account
                /time
                    /file

        :contract_order_book: ContractOrderBook Object

        :ret: None

        """
        timestamp = contract_order_book.timestamp
        contract_name = contract_order_book.short_name.replace(" ", "").replace(".", "")

        # Unique identifier for timestamp consisting of yy_mm_dd_hh
        time_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y_%m_%d_%H")
        # Unique identifier for the key for the map of contract ticker symbols to files. 
        file_key = "_ORDER"+"_contract"+contract_name+"time_"+time_str

        # Check if we are just updating a file vs. having to write a new one
        if file_key not in self.contract_ticker_symbol_to_files:
            # Create new folder
            if not os.path.exists('./data/%s/%s/' % (self.target, time_str)):
                os.makedirs('./data/%s/%s/' % (self.target, time_str))
            
            self.contract_ticker_symbol_to_files[file_key] = open('./data/%s/%s/%s.csv' % (self.target, time_str, self.file_str+file_key), 'w')
            
            # Create the writer
            write_file = self.contract_ticker_symbol_to_files[file_key]
            writer = csv.writer(write_file, delimiter=',')
            
            # Write the row headers
            writer.writerow(["ticker_symbol", "contract_name", "timestamp", "yes_orders", "no_orders"])
        else:
            write_file = self.contract_ticker_symbol_to_files[file_key]
            writer = csv.writer(write_file, delimiter=',')

        logging.info('Writing row for contract %s' % file_key)

        # Write the row
        writer.writerow([contract_order_book.ticker_symbol, contract_name, 
            contract_order_book.timestamp, 
            ", ".join(str(x) for x in contract_order_book.yes_orders), 
            ", ".join(str(x) for x in contract_order_book.no_orders)])
        write_file.flush()


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
