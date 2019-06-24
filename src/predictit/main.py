from predictit.db import RedisPredictItDb, ContractInfo, Contract
from predictit.api import PredictItAPI
from predictit.notifier import PredictItNotifier
from predictit.timeseries import ContractInfoTimeSeries
from predictit.exceptions import *
from redis.exceptions import *
import argparse
import time
import logging
import traceback
import requests
from threading import Thread
from predictit.models import TwitterMarket
import bs4
import os
import sys
import argparse

notifier = PredictItNotifier("alex.wlezien@gmail.com", "zHx#R%NQb9#*1*tz1LNu&tu3dK7!g", ["a.wlezien@gmail.com", "alex.dai186@gmail.com"])
api = PredictItAPI(notifier)
twitter_market = None
tweet_counts = {}
MAX_BUCKET_MAX_TWEETS = 10**9
MAX_BUY_ORDER = 0
EXECUTE_LIVE_TRADE = False
TWITTER_MARKET_GIVEN_INFO = None
PREDICTIT_USERNAME = None
PREDICTIT_PASSWORD = None
# ('How many tweets will @realDonaldTrump post from noon Mar. 13 to noon Mar. 20?', 'realDonaldTrump', 40868)

INFINITY = sys.maxsize

def setup():
    print('MAX_BUY_ORDER = %d' % MAX_BUY_ORDER)

    global twitter_market
    # global api
    logging.info('setup()')

    logging.info('api = %s' % api)
    logging.info('username = %s, password = %s' % (PREDICTIT_USERNAME, PREDICTIT_PASSWORD))
    api.create_authed_session(PREDICTIT_USERNAME, PREDICTIT_PASSWORD)
    # print('sending buy order')
    # api.buy_order(4390, False, 2, 99, MAX_BUY_ORDER, EXECUTE_LIVE_TRADE)
    all_markets = api.getRunningMarkets([TWITTER_MARKET_GIVEN_INFO])
    # we know there can only be one twitter market returned since twitter_market_given_info only gives one tuple
    twitter_market = [m for m in all_markets if isinstance(m, TwitterMarket)][0]
    logging.info('twitter markets = %s' % twitter_market)

    # for tm in twitter_markets:
    logging.info('Twitter Market = %s' % twitter_market)
    logging.info('Contracts = %s' % twitter_market.contracts)

    num_tweets = -1
    new_num_keyword_tweets=-1

    target_account = twitter_market.target_twitter_account
    if target_account == 'potus':
        num_tweets = api.getNumPotusTweets()
    elif target_account == 'realDonaldTrump' and not twitter_market.is_keyword_market:
        num_tweets = api.getNumTrumpTweets()
    elif target_account == 'realDonaldTrump' and twitter_market.is_keyword_market:
        num_tweets = api.getNumTrumpTweets()
        api.cacheCurrentTrumpTweets()
    elif target_account == 'vp':
        num_tweets = api.getNumPenceTweets()
    elif target_account == 'whitehouse':
        num_tweets = api.getNumWhitehouseTweets()
    elif target_account == 'Alexdai82109299' and not twitter_market.is_keyword_market:
        num_tweets = api.getNumAlexTestTweets()
    elif target_account == 'Alexdai82109299' and twitter_market.is_keyword_market:
        num_tweets = api.getNumAlexTestTweets()
        api.cacheCurrentAlexTweets()
        # new_num_keyword_tweets = 8

        # new_num_keyword_tweets = 8

    is_keyword_market = twitter_market.is_keyword_market
    if is_keyword_market:
        tweet_counts[target_account] = (num_tweets, twitter_market.starting_num_tweets)
    else:
        tweet_counts[target_account] = num_tweets

    for contract in twitter_market.contracts:

        short_name = contract.short_name
        min_tweets_in_contract = -1
        max_tweets_in_contract = -1

        if short_name[-1] == '-':
            min_tweets_in_contract = 0
            max_tweets_in_contract = int(short_name[:-1])
        elif short_name[-1] == '+':
            min_tweets_in_contract = int(short_name[:-1])
            max_tweets_in_contract = INFINITY
        # Handles shortnames for keyword markets
        elif len(short_name) == 1 and is_keyword_market:
            min_tweets_in_contract = int(short_name[0])
            max_tweets_in_contract = int(short_name[0])
        else:
            min_tweets_in_contract = int(short_name.split(' - ')[0])
            max_tweets_in_contract = int(short_name.split(' - ')[1])

        contract.min_tweets = min_tweets_in_contract
        contract.max_tweets = max_tweets_in_contract


def run_algorithms():
    global twitter_market
    assert twitter_market

    # for tm in twitter_markets:
    logging.info('------------------------------')
    target_account = twitter_market.target_twitter_account
    logging.info('target account = %s' % target_account)

    is_keyword_market = type(tweet_counts[target_account]) == tuple
    if is_keyword_market:
        old_tweets_total, old_keywords_total = tweet_counts[target_account]
    else:
        old_tweets_total = tweet_counts[target_account]

    new_tweets_total = -1
    new_keywords_total = -1

    if target_account == 'potus':
        new_tweets_total = api.getNumPotusTweets()
    elif target_account == 'realDonaldTrump' and not twitter_market.is_keyword_market:
        new_tweets_total = api.getNumTrumpTweets()
    elif target_account == 'realDonaldTrump' and twitter_market.is_keyword_market:
        new_tweets_total, new_keywords_total = api.getNumKeywordTweets('https://twitter.com/realDonaldTrump', twitter_market.keyword, old_tweets_total, old_keywords_total)
    elif target_account == 'vp':
        new_tweets_total = api.getNumPenceTweets()
    elif target_account == 'whitehouse':
        new_tweets_total = api.getNumWhitehouseTweets()
    elif target_account == 'Alexdai82109299' and not twitter_market.is_keyword_market:
        new_tweets_total = api.getNumAlexTestTweets()
    elif target_account == 'Alexdai82109299' and twitter_market.is_keyword_market:
        # Parse HTML HERE
        new_tweets_total, new_keywords_total = api.getNumKeywordTweets('https://twitter.com/Alexdai82109299', twitter_market.keyword, old_tweets_total, old_keywords_total)
        # update curr_num_trump_tweets = new_num_trump_tweets
    else:
        raise Exception('unrecognized target account, or possibly keyword markets are not supported for that account')
    # random sanity check that we're not reading wrong numbers due to multiple occurences of "profilenav-value"
    if abs(new_tweets_total - old_tweets_total) > 10:
        raise Exception("failed random sanity check that we're not reading wrong numbers due to multiple occurences of 'profilenav-value'")
    logging.info('previous number of tweets = %d' % old_tweets_total)
    logging.info('next number of tweets = %d' % new_tweets_total)

    should_place_trade = False
    if is_keyword_market:
        logging.info('analyzing tweet counts for KEYWORD market')
        # UPDATE NEXT COUNTS FOR KEYWORD TWEETS
        logging.info('previous number of keyword tweets = %d' % old_keywords_total)
        logging.info('next number of keyword tweets = %d' % new_keywords_total)
        if new_tweets_total > old_tweets_total:
            tweet_counts[target_account] = new_tweets_total, new_keywords_total
        if new_keywords_total > old_keywords_total:
            logging.info('new number of keyword tweets is greater than the current number for account = %s' % target_account)
            number_of_new_tweets = new_keywords_total - old_keywords_total
            relevant_num_tweets = new_keywords_total
            should_place_trade = True
    # else, it must be the case that this is not a keyword market. Then, only keep going if the number of new tweets is greater than previous,
    # since keywords don't matter
    elif new_tweets_total > old_tweets_total:
        logging.info('analyzing tweet counts for STANDARD market')
        logging.info('new number of tweets is greater than the current number for account = %s' % target_account)
        tweet_counts[target_account] = new_tweets_total
        number_of_new_tweets = new_tweets_total - old_tweets_total
        # Changed code for keyword markets
        relevant_num_tweets = new_tweets_total - twitter_market.starting_num_tweets
        should_place_trade = True

        # logging.info('Searching for bucket with %d keywords' % relevant_num_tweets)
    if should_place_trade:
        logging.info('searching contracts for trade')
        for contract in twitter_market.contracts:
            min_tweets_in_contract = contract.min_tweets
            max_tweets_in_contract = contract.max_tweets
            print(max_tweets_in_contract)
            if  (number_of_new_tweets > 0 and relevant_num_tweets == max_tweets_in_contract + 1) or (number_of_new_tweets == 2 and relevant_num_tweets == max_tweets_in_contract + 2):
                logging.info('crossed threshold for market="%s" on contract="%s", issuing buy no order' % (twitter_market.short_name, contract.short_name))
                # buy max no shares
                api.buy_order(contract.ticker_symbol, False, MAX_BUY_ORDER, 99, MAX_BUY_ORDER, EXECUTE_LIVE_TRADE)
            # elif relevant_num_tweets == max_tweets_in_contract:
                # buy less no shares
            # elif relevant_num_tweets == max_tweets_in_contract - 1:
                # buy even less no shares
            # elif relevant_num_tweets == max_tweets_in_contract - 2:
            #     # buy even even less no shares
            # elif relevant_num_tweets > min_tweets_in_contract and '+' in short_name:
            elif max_tweets_in_contract == INFINITY and ((number_of_new_tweets > 0 and relevant_num_tweets == min_tweets_in_contract) or (number_of_new_tweets == 2 and relevant_num_tweets == min_tweets_in_contract + 1)):
                logging.info('crossed threshold with market="%s" for contract="%s", issuing buy yes order because reached highest threshold' % (twitter_market.long_name, contract.short_name))
                api.buy_order(contract.ticker_symbol, True, MAX_BUY_ORDER, 99, MAX_BUY_ORDER, EXECUTE_LIVE_TRADE)


def start_while_loop():
    logging.info('starting while loop')

    while True:
        run_algorithms()


def start_predictit():
    # print('setup()')
    setup()
    start_while_loop()


def _parse_args():
    """
    Command-line arguments to the system.
    :return: the parsed args bundle
    """
    parser = argparse.ArgumentParser(description='main.py')
    parser.add_argument('--execute_live_trade', default=False, action='store_true', help='Activate whether we want actually execute trades on signal')
    parser.add_argument('--max_buy_order', type=int, default= 0, help='Determines the max buy order')
    parser.add_argument('--unique_id', type=int, default=1, help='Determines unique ID of instance')
    parser.add_argument('--target_account', type=str, required=True, help='Target twitter account to poll')
    parser.add_argument('--fake_target_account', type=str, default=None, help='Target twitter account to replace official twitter account for testing to poll')
    parser.add_argument('--starting_num_tweets', type=int, required=True, help='Number of starting tweet counts')
    parser.add_argument('--is_keyword_market', default=False, action='store_true', help='Whether or not to this is a keyword market')
    parser.add_argument('--keyword', type=str, default=None, help='Keyword tweet to parse in keyword markets')
    parser.add_argument('--start_date', type=str, required=True, help='Starting date of the market, in format "(Month Abbr).(space)%d"')
    parser.add_argument('--end_date', type=str, required=True, help='Ending date of the market, in format "(Month Abbr).(space)%d"')
    parser.add_argument('--username', type=str, required=True, help='Username for the predictit account')
    parser.add_argument('--password', type=str, required=True, help='Password for the predictit account')

    args = parser.parse_args()
    if bool(args.is_keyword_market) ^ bool(args.keyword):
        parser.error('--is_keyword_market requires --keyword and vice versa.')
    return args


#TWITTER_MARKET_GIVEN_INFO = ('How many tweets will @realDonaldTrump post from noon Mar. 13 to noon Mar. 20?', 'realDonaldTrump', 40868)

def main():
    global TWITTER_MARKET_GIVEN_INFO
    global PREDICTIT_USERNAME
    global PREDICTIT_PASSWORD
    global MAX_BUY_ORDER
    global EXECUTE_LIVE_TRADE
    args = _parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s - %(message)s',filename='predictit-logs-%d.txt' % args.unique_id)
    logging.info('starting PredictIt scraper...')

    EXECUTE_LIVE_TRADE = args.execute_live_trade
    MAX_BUY_ORDER = args.max_buy_order
    PREDICTIT_USERNAME = args.username
    PREDICTIT_PASSWORD = args.password

    if args.is_keyword_market:
    	TWITTER_MARKET_GIVEN_INFO = ('How many @{0} tweets mention "{1}" noon {2} - noon {3}?'.format(args.target_account,
    		args.keyword, args.start_date, args.end_date),
    		args.target_account if args.fake_target_account is None else args.fake_target_account, args.starting_num_tweets, args.is_keyword_market, args.keyword)
    else:
    	TWITTER_MARKET_GIVEN_INFO = ('How many tweets will @{0} post from noon {1} to noon {2}?'.format(args.target_account,
    		args.start_date, args.end_date),
    		args.target_account, args.starting_num_tweets, args.is_keyword_market)
    print ('twitter info = %s' % str(TWITTER_MARKET_GIVEN_INFO))
    start_predictit()

if __name__ == '__main__':
    main()

"""
Predictit Scraping
"""


    # old_keywords_total = api.getNumTrumpTweets()
    # twitter_markets = db.get_all_twitter_markets()
    # for tmgf in TWITTER_MARKET_GIVEN_INFO:

# def scrape_contract_info():
#     logger.info('new scrape')
#     all_contracts_info = api.getCurrentContractsInfo()
#     db.put_multiple_contracts_info(all_contracts_info)

# def do_scraping(scrape_time_interval):
#     while True:
#         try:
#             scrape_contract_info()
#         except APIError:
#             logger.error("failed to get contract info from API, retrying...")
#             continue
#         except RedisError:
#             logger.error("problem with Redis server while writing contract info data, retrying...")
#             continue
#         except Error:
#             logging.error('unknown error occurred, traceback below')
#             logging.error(traceback.format_exc())
#             continue
#         logger.info("done updating contracts info")
#         time.sleep(scrape_time_interval)
        # logger.info("getting volatile contracts")
        # all_contracts_stats = get_volatile_contracts()
        # for contract_stats in all_contracts_stats:
        #     logger.info("sending notification for contract with ticker symbol = %s" % contract.ticker_symbol)
        #     notifier.send_notification(contract,None)


# DB Stuff


# db = RedisPredictItDb('localhost', '6379')
# # connection = redis.ConnectionPool(host='localhost', port=6379)
