from predictit.db import RedisPredictItDb, ContractInfo, Contract
from predictit.api import PredictItAPI
from predictit.notifier import PredictItNotifier
from predictit.timeseries import ContractInfoTimeSeries
from predictit.exceptions import *
from predictit.db_static import *
from redis.exceptions import *
from predictit.proxy_server import start_proxy_server
import argparse
import time
import logging
import traceback
import requests
import threading
from threading import Thread
from predictit.models import TwitterMarket
import bs4
import os
import sys
import argparse
import queue

notifier = PredictItNotifier("alex.wlezien@gmail.com", "zHx#R%NQb9#*1*tz1LNu&tu3dK7!g", ["a.wlezien@gmail.com", "alex.dai186@gmail.com"])
long_running_api_instances = []
short_running_api_instances = []
 # = PredictItAPI(notifier,'http://localhost:8888')
db = None

# db = RedisPredictItDb('localhost', '6379')
# connection = redis.ConnectionPool(host='localhost', port=6379)
twitter_market = None
PREDICTIT_USERNAME = None
PREDICTIT_PASSWORD = None
INFINITY = sys.maxsize
ORDER_BOOK_SCRAPE_FREQ = None
VOLUME_SCRAPE_FREQ = None


def setup():
    global twitter_market
    global db
    global api_instances
    logging.info('setup()')
    logging.info('api = %s' % api)
    logging.info('username = %s, password = %s' % (PREDICTIT_USERNAME, PREDICTIT_PASSWORD))
    api.create_authed_session(PREDICTIT_USERNAME, PREDICTIT_PASSWORD)
    all_markets = api.getRunningMarkets([TWITTER_MARKET_GIVEN_INFO])



    logging.info("Setting up static db")
    db = FilePredictItDb(target=args.target_account, unique_id=args.unique_id,
    	start=args.start_date, end=args.end_date, agent_account=PREDICTIT_USERNAME)
    # we know there can only be one twitter market returned since twitter_market_given_info only gives one tuple
    twitter_market = [m for m in all_markets if isinstance(m, TwitterMarket)][0]

    long_running_api_instances = [PredictItApi()]
    # for tm in twitter_markets:
    logging.info('Twitter Market = %s' % twitter_market)
    logging.info('Contracts = %s' % twitter_market.contracts)


def scrape_order_book():
    print('scrape_order_book()')
    """
    Scrapes all of the ContractOrderBook data from the target Predictit contract.

    Starts a thread to scrape each bucket.
    """
    global twitter_market
    assert twitter_market

    logging.info('------------------------------')
    logging.info('Scraping Order Book Data for Target Market: %s' % twitter_market.contracts[0].long_name)

    current_time = time.time()
    contract_q = queue.Queue()
    threads = []

    for contract in twitter_market.contracts:
        contract_id = contract.ticker_symbol
        logging.info('Creating Thread for "%s" contract' % contract.short_name)
        t = threading.Thread(target=api.get_order_book_for_contract, args=(contract_id, contract.short_name, contract_q,), daemon=True)
        t.daemon = True
        logging.info('Starting Thread for "%s" contract' % contract.short_name)
        t.start()
        threads.append(t)
        t.timestamp = current_time
        logging.info('Ending Thread for "%s" contract' % contract.short_name)

    logging.info('joining threads...')
    for t in threads:
        while t.isAlive():
            print('checking if alive')
            t.join(1)
    # while threading.active_count() > 0:
        # time.sleep(0.1)



    # Write each contract to file
    while not contract_q.empty():
        row = contract_q.get()
        logging.info("Writing contract %s to csv file" % row.ticker_symbol)
        try:
        	db.put_contract_order_book(row)
        except Exception as e:
        	logging.info("Error occured when writing. Error: %s, Traceback: %s" % (e, traceback.extract_tb(e.__traceback__)))

    logging.info("Scraping Again")
    t = threading.Timer(ORDER_BOOK_SCRAPE_FREQ, scrape_order_book)
    t.setDaemon(True)
    t.start()


def scrape_volume_data():
    global twitter_market
    assert twitter_market

    logging.info('------------------------------')
    logging.info('Scraping Volume Data for Target Market: %s' % twitter_market.contracts[0].long_name)

    current_time = time.time()
    data = api.get_volume_data_for_market_24h(twitter_market.ticker_symbol)
    logging.info("Received data for volume data for ticker: %s" % twitter_market.ticker_symbol)

    db.put_market_volume(data)

    t = threading.Timer(VOLUME_SCRAPE_FREQ, scrape_volume_data)
    t.setDaemon(True)
    t.start()


def start_predictit():
    # print('setup()')
    setup()
    logging.info('Begin Scraping Loop')
    scrape_order_book()
    scrape_volume_data()
    while True:
        time.sleep(1000)


def _parse_args():
    """
    Command-line arguments to the system.
    :return: the parsed args bundle
    """
    parser = argparse.ArgumentParser(description='main.py')

    parser.add_argument('--unique_id', type=int, default=1, help='Determines unique ID of instance')
    parser.add_argument('--target_account', type=str, required=True, help='Target twitter account to poll')
    parser.add_argument('--start_date', type=str, required=True, help='Starting date of the market, in format "(Month Abbr).(space)%d"')
    parser.add_argument('--end_date', type=str, required=True, help='Ending date of the market, in format "(Month Abbr).(space)%d"')
    parser.add_argument('--username', type=str, required=True, help='Username for the predictit account')
    parser.add_argument('--password', type=str, required=True, help='Password for the predictit account')
    parser.add_argument('--order_book_scrape_freq', type=int, required=True, help='How frequently we want to scrape the Predictit Order book in seconds')
    parser.add_argument('--volume_scrape_freq', type=int, required=True, help='How frequently we want to scrape the Predictit Volume data in seconds')
    parser.add_argument('--is_keyword_market', default=False, action='store_true', help='Whether or not to this is a keyword market')
    parser.add_argument('--keyword', type=str, default=None, help='Keyword tweet to parse in keyword markets')

    args = parser.parse_args()
    return args


def main():
    global TWITTER_MARKET_GIVEN_INFO
    global PREDICTIT_USERNAME
    global PREDICTIT_PASSWORD
    global ORDER_BOOK_SCRAPE_FREQ
    global VOLUME_SCRAPE_FREQ
    global args
    args = _parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s - %(message)s',filename='predictit-logs-%d.txt' % args.unique_id)
    logging.info('starting PredictIt scraper...')

    PREDICTIT_USERNAME = args.username
    PREDICTIT_PASSWORD = args.password

    ORDER_BOOK_SCRAPE_FREQ = args.order_book_scrape_freq
    print(ORDER_BOOK_SCRAPE_FREQ)
    VOLUME_SCRAPE_FREQ = args.volume_scrape_freq

    if args.is_keyword_market:
        TWITTER_MARKET_GIVEN_INFO = ('How many @{0} tweets mention "{1}" noon {2} - noon {3}?'.format(args.target_account,
            args.keyword, args.start_date, args.end_date),
            args.target_account, 0, args.is_keyword_market, args.keyword)
    else:
        TWITTER_MARKET_GIVEN_INFO = ('How many tweets will @{0} post from noon {1} to noon {2}?'.format(args.target_account,
            args.start_date, args.end_date))
    # Replace("/", ")") handles formatting edge case ("4/12" instead of "Apr. 12"
    market_string = 'How many tweets will @{0} post from noon {1} to noon {2}?'.format(args.target_account,
            args.start_date, args.end_date)
    if "/" in market_string:
        market_string = market_string.replace("to", "-")

            args.target_account, 0, False)

    print ('twitter info = %s' % str(TWITTER_MARKET_GIVEN_INFO))

    start_proxy_server()
    start_predictit()

if __name__ == '__main__':
    main()
