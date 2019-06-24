# Imports
import time
import json
import codecs
import pytz
import logging
import urllib.request as urllib
from socket import error as SocketError
import errno
from urllib.error import *
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from predictit.models import *
from predictit.proxy_server import get_proxy_ips
from datetime import datetime
import dateutil.parser
from predictit.exceptions import *
import requests
import mechanicalsoup
import tweepy
import bs4
import traceback
import threading
import re
import queue
import random
	#def get_volume_for_time_period(self, unit, quantity):
	#	order_book = self.browser.get('https://www.predictit.org/api/Trade/7800/OrderBook').json()

'''
Provides fast and convenient access to the PredictIt API.
Data can be extracted in JSON/CSV format.

getHTML()
getJSON(makeFile=False)
makeJSON(data, staticInfo=False, makeFile=False)
makeCSV(data, staticInfo=False)
'''


class PredictItAPI(object):

    # Static Variables
    API_URL = 'https://www.predictit.org/api/marketdata/all/'
    STATIC_KEYS = ['id', 'longName', 'shortName', 'dateEnd', 'url']
    DYNAMIC_KEYS = ['timeStamp', 'bestBuyYesCost', 'bestBuyNoCost', 'bestSellYesCost', 'bestSellNoCost', 'lastTradePrice', 'lastClosePrice']
    EXTRA_DYNAMIC_KEYS = ['sharesTraded', 'todaysVolume', 'totalShares', 'todaysChange',
                    'buyYesData', 'sellYesData']

    HEADLESS_OPTIONS = Options()
    HEADLESS_OPTIONS.add_argument("--headless")
    HEADLESS_OPTIONS.add_argument("--window-size=1920x1080")
    driver = None

    TWITTER_CONSUMER_TOKEN ='E4XE7HZpccBapWGF5GUXfq5te'
    TWITTER_CONSUMER_SECRET = 'nFC65tDTRhxNtnVgzBzuCNsvP5KVFtjXOLd7zoDZHVNEwyI1zF'
    TWITTER_ACCESS_TOKEN = '1087850698937696257-vskw9aSreKjkmBOeGccc5oNNKkWWIs'
    TWITTER_ACCESS_TOKEN_SECRET = 'oguqjLZYm908DlEY46pL3gZkViWf3ndNjLgo5EQdyhffA'

    def __init__(self, notifier, proxy_broker_url=None):
        # consumer_token, consumer_secret, app_token, app_secret):
        # auth = tweepy.OAuthHandler(TWITTER_CONSUMER_TOKEN, TWITTER_CONSUMER_SECRET)
        # auth.access_token = TWITTER_ACCESS_TOKEN
        # auth.access_token_secret = TWITTER_ACCESS_TOKEN_SECRET
        # self.api = tweepy.API(auth)

        self.browser = mechanicalsoup.Browser()
        self.browser.session.headers.update({
    	  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36\
    	   (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}
    	)
        self.available = None
        self.access_token = None
        self.notifier = notifier
        self.cached_twitter_ids = set()

        self.proxy_urls = get_proxy_ips()
        self.proxy_broker_url = proxy_broker_url

    def update_balances(self):
        r = self.browser.get('https://www.predictit.org/api/Account/Status')
        user_funds = r.json()
        # print('user funds = %s' % user_funds)
        logging.info('REQUEST: /Account/Status, received status code = %d, content = %s' % (r.status_code,user_funds))
        self.available = int(user_funds['accountBalanceDecimal'] * 100)
        logging.info('updated balance to %d' % self.available)
        	#self.gain_loss = user_funds['SharesText']
        	#self.invested = user_funds['PortfolioText']

    def money_available(self):
        self.update_balances()
        print(("You have %s" % self.available) + "available.")

    def max_num_shares_buyable_at_price(self, price, MAX_BUY_ORDER):
        balance = self.available
        max_num_shares = min(MAX_BUY_ORDER*100//99, int(balance / 99))
        logging.info('calculated max shares of %d for a balance of %d and price of %d cents' % (max_num_shares,balance,price))
        return max_num_shares

    def __validate_login(self, response):
        assert 'access_token' in str(response.content), "Invalid login."

    def get_new_api_token(self,username,password):
        login_page = self.browser.get('https://www.predictit.org')
        r = self.browser.post('https://www.predictit.org/api/Account/token',
        		{'email': username,
        		'password': password,
        		'grant_type': 'password',
        		'rememberMe': 'false'})
        self.__validate_login(r)
        print(r.json())
        self.access_token = r.json()['access_token']
        return self.access_token

    REFRESH_RATE = 60*60*4
    def refresh_new_api_token_thread(self,username,password):
        t = threading.Timer(self.REFRESH_RATE, self.refresh_new_api_token_thread, [username, password])
        t.setDaemon(True)
        t.start()
        self.browser.session.headers.update({'Authorization': 'Bearer %s' % self.get_new_api_token(username,password)})
        self.update_balances()

    def create_authed_session(self, username, password):
        logging.info('creating new authed session')

        self.browser.session.headers.update({'Authorization': 'Bearer %s' % self.get_new_api_token(username,password)})
        self.update_balances()

        t = threading.Timer(self.REFRESH_RATE, self.refresh_new_api_token_thread, [username, password])
        t.setDaemon(True)
        t.start()

        return self.browser

    def get_random_proxy_url(self):
        ind = random.randint(0,len(self.proxy_urls) - 1)
        return 'http://%s:%s' % (self.proxy_urls[ind][0], self.proxy_urls[ind][1])

    def get_order_book_for_contract(self, cid, short_name, q):
        logging.info('getting order book from url for cid = %d' % cid)
        sent_request_time = time.clock()
        logging.info('done getting time.time()')
        proxy_url = self.get_random_proxy_url()
        print('proxy url: %s' % proxy_url)
        # self.browser.session.proxies = {'http':self.proxy_broker_url}
        r = self.browser.get('https://www.predictit.org/api/Trade/%d/OrderBook' % cid,timeout=5)
        print(r)
        print(r.content)
        order_book = r.json()
        logging.info('finished getting order book from url for cid = %d' % cid)
        yes_orders_raw = order_book['yesOrders']
        no_orders_raw = order_book['noOrders']
        yes_orders = []
        no_orders = []
        for o_dct in yes_orders_raw:
            yes_orders.append(Order(o_dct['contractId'],True,o_dct['pricePerShare'],o_dct['quantity']))
        for o_dct in no_orders_raw:
            no_orders.append(Order(o_dct['contractId'],False,o_dct['pricePerShare'],o_dct['quantity']))
        q.put(ContractOrderBook(cid, short_name, sent_request_time,yes_orders,no_orders))
        q.task_done()

    def get_volume_data_for_market_24h(self, ticker_symbol):
        proxy_url = self.get_random_proxy_url()
        # self.browser.session.proxies = {'http':self.proxy_broker_url}
        volume_data = self.browser.get('https://www.predictit.org/api/Public/GetMarketChartData/%d?timespan=24h&showHidden=true' % ticker_symbol).json()
        print(volume_data)
        # print('_____')
        # print(cid)
        contract_list = [ContractVolumeData(vd['contractId'], dateutil.parser.parse(vd['date']).timestamp(),
                vd['tradeVolume'], vd['contractName'], vd['contractId']) for vd in volume_data]
        market_volume_data = MarketVolumeData(volume_data[0]['marketId'], contract_list[0].timestamp, contract_list)
        return market_volume_data

    def confirm_trade(self, cid, is_yes_order, quantity, price, MAX_BUY_ORDER, EXECUTE_LIVE_TRADE):
        trade_info = {
        		'quantity': quantity,
        		'pricePerShare': price,
        		'contractId': cid,
        		'tradeType': 1 if is_yes_order else 0
        }
        r = self.browser.post('https://www.predictit.org/api/Trade/ConfirmTrade', trade_info)
        print(r.content)
        # logging.info('REQUEST: ConfirmTrade, received status code = %d, content=%s' % (r.status_code, r.content))
        #
        # if EXECUTE_LIVE_TRADE:
        #     r = self.browser.post('https://www.predictit.org/api/Trade/SubmitTrade', trade_info)
        #     logging.info('REQUEST: SubmitTrade, received status code = %d, content=%s' % (r.status_code, r.content))
        # else:
        #     logging.info('REQUEST: NO EXECUTE LIVE TRADE')
        #
        # self.update_balances()

    #type(cid) = int
    def buy_order(self, cid, is_yes_order, quantity, price, MAX_BUY_ORDER, EXECUTE_LIVE_TRADE):
        logging.info('executing buy order at cid=%d, quantity=%d, price=%d, order type=%s' % (cid, quantity, price, 'yes' if is_yes_order else 'no'))
        max_quantity = self.max_num_shares_buyable_at_price(price, MAX_BUY_ORDER)
        # temporarily buy max shares until we want to be able to moderate.
        # quantity = max_quantity + 1
        if quantity > max_quantity:
            logging.warning('quantity "%d" was greater than REQUIRED quantity "%d", reset' % (quantity, max_quantity))
            quantity = max_quantity
        # quantity = 1
        trade_info = {
        		'quantity': quantity,
        		'pricePerShare': price,
        		'contractId': cid,
        		'tradeType': 1 if is_yes_order else 0
        }
        # r = self.browser.post('https://www.predictit.org/api/Trade/ConfirmTrade', trade_info)
        # logging.info('REQUEST: ConfirmTrade, received status code = %d, content=%s' % (r.status_code, r.content))

        if EXECUTE_LIVE_TRADE:
            r = self.browser.post('https://www.predictit.org/api/Trade/SubmitTrade', trade_info)
            logging.info('REQUEST: SubmitTrade, received status code = %d, content=%s' % (r.status_code, r.content))
        else:
            logging.info('REQUEST: NO EXECUTE LIVE TRADE')

        self.update_balances()
        # logging.info(r.content)


    # def sell_order(self, cid, is_yes_order, price):
    #     logging.info('starting sell order at cid=%d, price=%d, order type=%s...' % (cid, price, 'yes' if is_yes_order else 'no'))
    #     # max_quantity = self.max_num_shares_buyable_at_price(price)
    #     trade_info = {
    #     		'quantity': 1000,
    #     		'pricePerShare': price,
    #     		'contractId': cid,
    #     		'tradeType': 1 if is_yes_order else 0
    #     }
    #     r = self.browser.post('https://www.predictit.org/api/Trade/ConfirmTrade', trade_info)
    #     logging.info(r.content)
    #     r = self.browser.post('https://www.predictit.org/api/Trade/SubmitTrade', trade_info)
    #     self.update_balances()
    #     logging.info(r.content)


    '''Returns an HTML copy of the PredictIt API webpage using a non-headless Selenium browser'''
    def getHTML(self):
        self.driver = webdriver.Chrome(chrome_options=self.HEADLESS_OPTIONS)
        self.driver.get(self.API_URL)
        self.driver.find_element_by_tag_name('MarketList')   # Wait until site is fully loaded
        html = self.driver.page_source

        print('Completed: getHTML')
        return html

    def getRunningMarkets(self, twitter_markets_given_info):
        api_json = self.getJSON()

        markets = []

        for market_dict in api_json:
            # print(market_dict)
            market = None
            for tmgf in twitter_markets_given_info:
                is_keyword_market = tmgf[3]
                if market_dict['name'] == tmgf[0]:
                    market = TwitterMarket(ticker_symbol=market_dict['id'], long_name=market_dict['name'], short_name=market_dict['shortName'],
                                image_url=market_dict['image'], url=market_dict['url'], status=market_dict['status'], target_twitter_account=tmgf[1],
                                 starting_num_tweets=tmgf[2],keyword=tmgf[4] if is_keyword_market else None)
            if market is None:
                market = Market(ticker_symbol=market_dict['id'], long_name=market_dict['name'], short_name=market_dict['shortName'],
                        image_url=market_dict['image'], url=market_dict['url'], status=market_dict['status'])
            for contract_dict in market_dict['contracts']:
                # print(json.dumps(contract_dict,indent=4))
                contract = None
                if isinstance(market, TwitterMarket):
                    contract = Contract(ticker_symbol=contract_dict['id'], long_name=contract_dict['longName'],
                                    short_name=contract_dict['shortName'],
                                    time_end=contract_dict['dateEnd'] if contract_dict['dateEnd'] == 'N/A' else dateutil.parser.parse(contract_dict['dateEnd']).timestamp(),
                                    image_url=contract_dict['image'], status=contract_dict['status'])
                market.contracts.append(contract)
            markets.append(market)
        return markets

    TRUMP_PAGE_URL = ""
    # def getNumTweetsGenericFromSpecificDate(self, date_time, url):
    #
    #
    # def getNumTrumpTweetsFromSpecificDate(self, date_time):
    #     return self.getNumTweetsGenericFromSpecificDate(date_time, )

    LAST_EMAIL_EXCEPTION_TIME = -100
    LAST_EMAIL_503_TIME = -100
    EMAIL_INTERVAL = 60
    REQUEST_WAIT_TIME = 5


    def poll_twitter(self, url):
        status_code = 503
        while status_code != 200:
            try:
                # REMOVE
                # curr_time = time.time()
                r = requests.get(url)
                # end = time.time()
                # logging.info("Time to do request:%0.4f" % (end-curr_time))
                status_code = r.status_code
                if status_code != 200:
                    logging.info('REQUEST: %s, received status code = %d, content = %s, retrying after %d seconds...' % (url,r.status_code,'',self.REQUEST_WAIT_TIME))
                    curr_time = time.time()
                    if curr_time - self.LAST_EMAIL_503_TIME > self.EMAIL_INTERVAL:
                        self.LAST_EMAIL_503_TIME = curr_time
                        logging.info('ERROR: 503 Encountered: Sending email...')
                        self.notifier.send_notification('%s: HTTP 503 error occurred when pinging Twitter' % curr_time, "503 Encountered")
                    time.sleep(self.REQUEST_WAIT_TIME)
            except Exception as e:
                traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                logging.info('ERROR: %s, stack_trace = %s, retrying after %d seconds...' % (e, traceback_str, self.REQUEST_WAIT_TIME))
                curr_time = time.time()
                if curr_time - self.LAST_EMAIL_EXCEPTION_TIME > self.EMAIL_INTERVAL:
                    self.LAST_EMAIL_EXCEPTION_TIME = curr_time
                    print(e, curr_time)
                    self.notifier.send_error_notification(e, curr_time)
                time.sleep(self.REQUEST_WAIT_TIME)
        return r

    def cacheCurrentTweetsGeneric(self, url):
        logging.info('caching current tweets for url = %s' % url)
        r = self.poll_twitter(url)
        html = r.content
        logging.info('REQUEST: %s, received status code = %d, content = %s' % (url,r.status_code,''))
        soup = bs4.BeautifulSoup(html, 'lxml')
        tweet_boxes = soup.findAll('div', {"data-tweet-id": True})
        # print(twe)
        for tb in tweet_boxes:
            # print (tb.attrs)
            tweet_id = tb['data-tweet-id']
            self.cached_twitter_ids.add(tweet_id)
            if tb.has_attr('data-retweet-id'):
                retweet_id = tb['data-retweet-id']
                self.cached_twitter_ids.add(retweet_id)
        logging.info('cached %d tweet ids' % len(tweet_boxes))

    def cacheCurrentTrumpTweets(self):
        self.cacheCurrentTweetsGeneric('https://twitter.com/realDonaldTrump')

    def cacheCurrentAlexTweets(self):
        self.cacheCurrentTweetsGeneric('https://twitter.com/Alexdai82109299')

    def cacheCurrentPenceTweets(self):
        self.cacheCurrentTweetsGeneric('https://twitter.com/vp')

    def cacheCurrentPotusTweets(self):
        self.cacheCurrentTweetsGeneric('https://twitter.com/potus')

    def cacheCurrentWhitehouseTweets(self):
        self.cacheCurrentTweetsGeneric('https://twitter.com/whitehouse')

    def getNumTweetsGeneric(self, url):
        logging.info('getting number of tweets for url = %s' % url)
        r = self.poll_twitter(url)
        html = r.content
        logging.info('REQUEST: %s, received status code = %d, content = %s' % (url,r.status_code,''))
        soup = bs4.BeautifulSoup(html, 'lxml')
        target = soup.find('span', {'class': 'ProfileNav-value'})
        num_tweets = int(target['data-count'])
        logging.info('returning %d tweets for %s' % (num_tweets,url))

        # end = time.time()

        #  logging.info("Time to do html parsing:%0.4f" % (end-curr_time))
        return num_tweets


    def getNumAlexTestTweets(self):
        logging.info('getting number of test tweets...')
        new_tweets_total = self.getNumTweetsGeneric('https://twitter.com/Alexdai82109299')
        return new_tweets_total


    def getNumPotusTweets(self):
        logging.info('getting number of potus tweets...')
        new_tweets_total = self.getNumTweetsGeneric('https://twitter.com/potus')
        return new_tweets_total

    def getNumWhitehouseTweets(self):
        logging.info('getting number of whitehouse tweets...')
        new_tweets_total = self.getNumTweetsGeneric('https://twitter.com/whitehouse')
        return new_tweets_total

    def getNumPenceTweets(self):
        logging.info('getting number of pence tweets...')
        new_tweets_total = self.getNumTweetsGeneric('https://twitter.com/vp')
        return new_tweets_total

    def getNumTrumpTweets(self):
        logging.info('getting number of trump tweets...')
        new_tweets_total = self.getNumTweetsGeneric('https://twitter.com/realDonaldTrump')
        return new_tweets_total

    def getLatestTrumpTweets(self):
        html = requests.get('https://twitter.com/realDonaldTrump').content
        soup = bs4.BeautifulSoup(html, 'lxml')
        return None

    # def __scrollPage(self):
    #     SCROLL_PAUSE_TIME = 0.5
    #
    #     # Get scroll height
    #     last_height = driver.execute_script("return document.body.scrollHeight")
    #     num_scrolls
    #     while True:
    #         # Scroll down to bottom
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #
    #         # Wait to load page
    #         time.sleep(SCROLL_PAUSE_TIME)
    #
    #         # Calculate new scroll height and compare with last scroll height
    #         new_height = driver.execute_script("return document.body.scrollHeight")
    #         if new_height == last_height:
    #             break
    #         last_height = new_height
    # def getTotalNumKeywordTweets(self, url, keyword):
    #     logging.info('counting total number of tweets with "%s" in %s...' % (keyword, url))
    #     browser = selenium.ChromeDriver()
    #     browser

    def getNumKeywordTweets(self, url, keyword, old_tweets_total, old_keywords_total):
        logging.info('getting NEW number of tweets with "%s" in %s...' % (keyword, url))

        r = self.poll_twitter(url)

        html = r.content
        logging.info('REQUEST: %s, received status code = %d, content = %s' % (url,r.status_code,''))
        soup = bs4.BeautifulSoup(html, 'lxml')
        results = soup.findAll('a', {'data-nav': 'tweets'})
        elem = results[0]
        target = elem.findAll('span', {'class': 'ProfileNav-value'})[0]

        new_tweets_total = int(target['data-count'])
        new_keywords_total = old_keywords_total

        if new_tweets_total > old_tweets_total:
            # tweet_boxes= soup.findAll('li', {"class": "js-stream-item stream-item stream-item"})


                # all_tweets.append((text, timestamp, tweet_id))
            # all_tweets.sort(reverse=True, key=lambda x: x[1])


            # for i in range(new_tweet_diff):
            #     search = re.search("(?i)(%s)"%keyword, all_tweets[i][0])
            #     logging.info(search)
            #     if search:
            #         logging.info('Keyword Match Found in %d-th most recent tweet:String: %s' %
            #             (new_tweet_diff, all_tweets[i][0]))
            #         counts += 1
            new_keywords_total += self.countNumKeywordTweetsOnPage(soup,keyword)

        ### NEED TO FIND HOW TO HANDLE CHRONOLOGICAL ORDER AND PROMOTED TWEET COUNTS

        return new_tweets_total, new_keywords_total

    def countNumKeywordTweetsOnPage(self, soup, keyword):
        tweet_boxes = soup.findAll('div', {"data-tweet-id": True})
        all_tweets = []
        counts = 0
        for tb in tweet_boxes:
            timestamp = tb.findAll(attrs={"data-time-ms":True})[0]['data-time-ms']
            text = tb.findAll('p', {"class": "TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"})[0].text
            tweet_id = tb['data-tweet-id']
            should_count_tweet = False
            # handle standard case of normal tweet
            if tweet_id not in self.cached_twitter_ids:
                self.cached_twitter_ids.add(tweet_id)
                should_count_tweet = True
            # check if this tweet is actually a retweet, aka has a retweet id and thus must be recorded differently.
            # cases should be exclusive in case of normal tweet followed by rapid retweet.
            elif tb.has_attr('data-retweet-id') and tb['data-retweet-id'] not in self.cached_twitter_ids:
                self.cached_twitter_ids.add(tb['data-retweet-id'])
                should_count_tweet = True

            if should_count_tweet:
                tweet_contains_keyword = re.search("(?i)(%s)"%keyword, text)
                logging.info('search results = %s' % tweet_contains_keyword)
                if tweet_contains_keyword:
                    logging.info('Keyword Match Found in tweet with id %s:String: %s' %
                                (tweet_id, text))
                    counts += 1
        return counts

    def getCurrentContractsInfo(self):
        api_json = self.getJSON()
        # print(api_json)
        contracts_info = []

        for market in api_json:
            for contract_info_dict in market['contracts']:
                naive_dt = dateutil.parser.parse(market['timeStamp'])
                tz = pytz.timezone('US/Eastern')
                eastern_dt = tz.normalize(tz.localize(naive_dt))

                best_buy_yes_cost = contract_info_dict['bestBuyYesCost']
                best_buy_no_cost = contract_info_dict['bestBuyNoCost']
                best_sell_yes_cost = contract_info_dict['bestSellYesCost']
                best_sell_no_cost = contract_info_dict['bestSellNoCost']
                last_trade_price = contract_info_dict['lastTradePrice']
                last_close_price = contract_info_dict['lastClosePrice']

                if best_buy_yes_cost is None:
                    best_buy_yes_cost = -1
                else:
                    best_buy_yes_cost = int(float(best_buy_yes_cost) * 100)
                if best_buy_no_cost is None:
                    best_buy_no_cost = -1
                else:
                    best_buy_no_cost = int(float(best_buy_no_cost) * 100)
                if best_sell_yes_cost is None:
                    best_sell_yes_cost = -1
                else:
                    best_sell_yes_cost = int(float(best_sell_yes_cost) * 100)
                if best_sell_no_cost is None:
                    best_sell_no_cost = -1
                else:
                    best_sell_no_cost = int(float(best_sell_no_cost) * 100)
                if last_trade_price is None:
                    last_trade_price = -1
                else:
                    last_trade_price = int(float(last_trade_price) * 100)
                if last_close_price is None:
                    last_close_price = -1
                else:
                    last_close_price = int(float(last_close_price) * 100)

                contract_info = ContractInfo(ticker_symbol=contract_info_dict['id'], best_buy_yes_cost= best_buy_yes_cost,
                                                best_buy_no_cost=best_buy_no_cost,  best_sell_yes_cost=best_sell_yes_cost,
                                                best_sell_no_cost=best_sell_no_cost, last_trade_price=last_trade_price,last_close_price=last_close_price,
                                                timestamp=eastern_dt.timestamp(), timestamp_as_date=eastern_dt)
                # timestamp=datetime.strptime(market['TimeStamp'], '%Y-%m-%dT%H:%M:%S.%f'))
                contracts_info.append(contract_info)

        return contracts_info

    '''Returns a JSON copy of the PredictIt API webpage using a headless urllib browser'''
    def getJSON(self, makeFile=False):
        try:
            resource = urllib.urlopen(self.API_URL)
            data = resource.read().decode(resource.headers.get_content_charset()) # Gets only the visible page text
        except URLError:
            raise APIError()
        data = json.loads(data)                     # Converts to JSON
        # print("JSON data from API = %s" % data)
        # print ("adsdiofjsf")
        # logging.warning ("abdfsdf please show up")
        data = data['markets']                      # Access only the 'Markets' information

        if makeFile:
            codecs.open('markets.json', 'w', encoding='utf8').write(json.dumps(data, indent=4))

        print('Completed: getJSON')
        return data

    '''Separates the JSON output into each contract's static and dynamic components.
    Returns the separated JSON data and makes a file if requested.'''
    def makeJSON(self, data, staticInfo=False, makeFile=False):

        # self.driver = webdriver.Chrome(chrome_options=self.HEADLESS_OPTIONS)
        fileName = ""
        result = []
        keys = []

        if (staticInfo):
            keys = API.STATIC_KEYS
            fileName = "static.json"

        else:
            keys = []
            keys.extend(API.DYNAMIC_KEYS)
            keys.remove('timeStamp')                # Prevents an error; already accounted for in line 56
            fileName = "dynamic.json"

        for market in data[:2]:
            for contract in market['contracts']:
                try:
                    contract_info = {}
                    contract_info['timeStamp'] = market['timeStamp']

                    for key in keys:
                        contract_info[key] = contract[key]

                    contract_info = self.getMarketPageData(contract_info, contract['url'])
                    result.append(contract_info)

                except Exception:
                    import traceback
                    traceback.print_exc()

        if makeFile:
            codecs.open(fileName, 'w+', encoding='utf8').write(json.dumps(result, indent=4))

        print('Completed: makeJSON')
        return result

    '''Accesses Market-Pages to access more specific values. Returns an updated contract_info variable.'''
    def getMarketPageData(self, contract_info, URL):

        self.driver.get(URL)

        table = self.driver.find_element_by_xpath("//TABLE[@class='table table-condensed table-striped table-info']")
        values = table.find_elements_by_tag_name("td")
        values = [value.get_attribute('innerHTML') for value in values]
        values = values[-8:]
        try:
            contract_info["sharesTraded"] = values[1].split(",")[0]
            contract_info["todaysVolume"] = values[3].split(",")[0]
            contract_info["totalShares"] = values[5].split(",")[0]
            contract_info["todaysChange"] = values[7].split("<")[0]

        except Exception as e:
            print("---")
            print(URL)
            print(e.message)

            for i, v  in enumerate(values):
                print(i)
                print(v)
                print("\n")
            print("---")

        if values[7] == "NC":       # No change
            contract_info["TodaysChange"] = 0

        self.driver.find_element_by_id("getPrices").click()
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, "(//DIV[@class='col-lg-5 col-md-5'])[2]")))

        yesTable = self.driver.find_element_by_xpath("(//DIV[@class='col-lg-5 col-md-5'])[2]")
        yesValues = yesTable.find_elements_by_tag_name("td")
        yesValues = [yesValue.get_attribute('innerText') for yesValue in yesValues]
        yesValues = yesValues[5:]

        buyYesPrices = yesValues[0::5]
        buyYesShares = yesValues[1::5]
        sellYesPrices = yesValues[3::5]
        sellYesShares = yesValues[4::5]

        buyYesPrices = [buyYesPrice[:-1] for buyYesPrice in buyYesPrices]
        sellYesPrices = [sellYesPrice[:-1] for sellYesPrice in sellYesPrices]

        buyYesPrices = [0 if value == '' else value for value in buyYesPrices]
        buyYesShares = [0 if value == '' else value for value in buyYesShares]
        sellYesPrices = [0 if value == '' else value for value in sellYesPrices]
        sellYesShares = [0 if value == '' else value for value in sellYesShares]

        buyYesPrices = map(int, buyYesPrices)
        buyYesShares = map(int, buyYesShares)
        sellYesPrices = map(int, sellYesPrices)
        sellYesShares = map(int, sellYesShares)

        # noTable = self.driver.find_element_by_xpath("(//DIV[@class='col-lg-5 col-md-5'])[3]")
        # noValues = noTable.find_elements_by_tag_name("td")
        # noValues = [noValue.get_attribute('innerText') for noValue in noValues]
        # noValues = noValues[5:]
        #
        # buyNoPrices = noValues[0::5]
        # buyNoShares = noValues[1::5]
        # sellNoPrices = noValues[3::5]
        # sellNoShares = noValues[4::5]
        #
        # buyNoPrices = [buyNoPrice[:-1] for buyNoPrice in buyNoPrices]
        # sellNoPrices = [sellNoPrice[:-1] for sellNoPrice in sellNoPrices]
        #
        # buyNoPrices = [0 if value == '' else value for value in buyNoPrices]
        # buyNoShares = [0 if value == '' else value for value in buyNoShares]
        # sellNoPrices = [0 if value == '' else value for value in sellNoPrices]
        # sellNoShares = [0 if value == '' else value for value in sellNoShares]
        #
        # buyNoPrices = map(int, buyNoPrices)
        # buyNoShares = map(int, buyNoShares)
        # sellNoPrices = map(int, sellNoPrices)
        # sellNoShares = map(int, sellNoShares)

        buyYesData = dict(zip(buyYesPrices, buyYesShares))
        sellYesData = dict(zip(sellYesPrices, sellYesShares))
        # buyNoData = dict(zip(buyNoPrices, buyNoShares))
        # sellNoData = dict(zip(sellNoPrices, sellNoShares))

        contract_info['buyYesData'] = buyYesData
        contract_info['sellYesData'] = sellYesData
        # contract_info['BuyNoData'] = buyNoData
        # contract_info['SellNoData'] = sellNoData

        return contract_info

    '''Converts the JSON data into a CSV file.'''
    def makeCSV(self, data, staticInfo=False):
        fileName = ""
        keys = []

        if (staticInfo):
            keys = API.STATIC_KEYS
            fileName = "static.csv"

        else:
            keys = API.DYNAMIC_KEYS
            fileName = "dynamic.csv"

        file = codecs.open(fileName, 'w+', encoding='utf8')

        # Static info requires quotation marks around each value
        if staticInfo:
            entry = []
            for key in keys:
                entry.append("'%s'" % key)
            entry = ",".join(entry)
            file.write(entry + "\n")

            for contract in data:
                entry = []                          # Contract entry
                for key in keys:
                    if contract[key] != None:       # Replace null values with empty strings so database can process
                        entry.append("'%s'" % contract[key])

                    else:
                        entry.append("''")

                entry = ",".join(entry)
                file.write(entry + "\n")

        # Dynamic info does not require quotation marks
        else:
            entry = []
            for key in keys:
                entry.append("%s" % key)

            entry = ",".join(entry)
            file.write(entry + "\n")

            for contract in data:
                entry = []                          # Contract entry
                for index, key in enumerate(keys):
                    if contract[key] != None:       # Replace null values with empty strings so database can process
                        try:                        # If value is number, multiple by 100
                            if (contract[key] < 1):
                                contract[key] = int(contract[key]*100)
                        except:
                            pass
                        entry.append("%s" % contract[key])

                    else:
                        entry.append("")

                entry = ",".join(entry)
                file.write(entry + "\n")

        file.close()
        print('Completed: makeCSV')


# t0 = time.time()
# # --
# # Collect data
# API = API()
# JSON = API.getJSON()
#
# # Build static information
# # STATIC_INFO = API.makeJSON(JSON, staticInfo=True)
# # API.makeCSV(STATIC_INFO, staticInfo=True)
#
# # Build dynamic information
# DYNAMIC_INFO = API.makeJSON(JSON, staticInfo=False, makeFile=True)
# # API.makeCSV(DYNAMIC_INFO, staticInfo=False)
# # --
# t1 = time.time()
# print(t1-t0)
