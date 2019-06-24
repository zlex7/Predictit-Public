import pytest
import datetime
import dateutil
import pytz
import random
from predictit.api import PredictItAPI
from predictit.models import TwitterMarket, Contract
from predictit.main import run_algorithms
import predictit.main
from unittest.mock import call


mock_num_trump_tweets = 0
mock_num_pence_tweets = 0
mock_num_whitehouse_tweets = 0
mock_num_potus_tweets = 0
buy_order_called_states = {}
cid_to_mid = {}
num_buy_orders = 0

PROBABILITY_OF_TWEET = 0.25
MAX_NUM_SHARES_TO_BUY = 1000

def mockNumPotusTweets():
    global mock_num_potus_tweets

    # seqlen = 10000
    # seq= [random.random() for _ in np.arange(seqlen)]
    num = random.random()
    if num < PROBABILITY_OF_TWEET:
        mock_num_potus_tweets += 1
    return mock_num_potus_tweets

def mockNumPenceTweets():
    global mock_num_pence_tweets

    # seqlen = 10000
    # seq= [random.random() for _ in np.arange(seqlen)]
    num = random.random()
    if num < PROBABILITY_OF_TWEET:
        mock_num_pence_tweets += 1
    return mock_num_pence_tweets

def mockNumWhitehouseTweets():
    # print('in mockNumWhitehouseTweets')
    global mock_num_whitehouse_tweets

    # seqlen = 10000
    # seq= [random.random() for _ in np.arange(seqlen)]
    num = random.random()
    if num < PROBABILITY_OF_TWEET:
        mock_num_whitehouse_tweets += 1
    return mock_num_whitehouse_tweets

def mockNumTrumpTweets():
        # global num_buy_orders

    global mock_num_trump_tweets
    print('generating trump tweet')
    # seqlen = 10000
    # seq= [random.random() for _ in np.arange(seqlen)]
    num = random.random()
    if num < PROBABILITY_OF_TWEET:
        # print('incrementing trump tweets')
        mock_num_trump_tweets += 1
    return mock_num_trump_tweets
    # tweets = [0]*seqlen
    # count=0
    # for i, num in enumerate(seq):
    #     if num < 0.05:
    #         count+=1
            # tweets[i]=count

def mock_buy_order(cid, is_yes_order, quantity, price, MAX_BUY_ORDER, EXECUTE_LIVE_TRADE):
    global num_buy_orders
    print('calling mock_buy_order unique')
    relevant_tweets = -1
    if cid_to_mid[cid] == 1116:
        relevant_tweets = mock_num_trump_tweets
    elif cid_to_mid[cid] == 1115:
        relevant_tweets = mock_num_whitehouse_tweets
    print('cid_to_mid = %s' % cid_to_mid)
    buy_order_called_states[cid_to_mid[cid]].append(relevant_tweets)#{'cid': cid, 'is_yes_order': is_yes_order, 'quantity': quantity, 'price': price})
    num_buy_orders += 1

def mock_max_num_shares_buyable_at_price(price):
    return MAX_NUM_SHARES_TO_BUY

# @pytest.mark.parametrize("mock_json,expected", [
    #     (   [ContractInfo(ticker_symbol='test contract info', best_buy_yes_cost='20',
#             best_buy_no_cost='80',  best_sell_yes_cost='19',
#             best_sell_no_cost='79', last_trade_price='19',
#             last_close_price='15', timestamp=pytz.timezone('US/Eastern').normalize(pytz.timezone('US/Eastern').localize(dateutil.parser.parse('2019-01-18T17:10:49.989945'))).timestamp(),
#             timestamp_as_date=pytz.timezone('US/Eastern').normalize(pytz.timezone('US/Eastern').localize(dateutil.parser.parse('2019-01-18T17:10:49.989945'))))],
#
#     )
# ])
def test_main_loop(mocker):
    global mock_num_trump_tweets
    global mock_num_pence_tweets
    global mock_num_whitehouse_tweets
    global mock_num_potus_tweets
    global buy_order_called_states
    global num_buy_orders
    global cid_to_mid

    mock_json_function = mocker.patch('predictit.api.PredictItAPI.getJSON')
    predictit.main.twitter_market =TwitterMarket(ticker_symbol=1116, long_name='twitter market long name 1', short_name='twitter market short name 1',
            image_url='imgurl', url='url', status='OPEN', target_twitter_account='trump',
            starting_num_tweets=800, contracts=[Contract(ticker_symbol=1111,short_name='80 - 83',min_tweets=80,max_tweets=83),Contract(ticker_symbol=1112,short_name='84 - 87',min_tweets=84,max_tweets=87), Contract(ticker_symbol=1113,short_name='88 - 91',min_tweets=88,max_tweets=91), Contract(ticker_symbol=1114,short_name='92+',min_tweets=92,max_tweets=predictit.main.INFINITY)])
         #     TwitterMarket(ticker_symbol=1115, long_name='twitter market long name 2', short_name='twitter market short name 2',
         # image_url='imgurl', url='url', status='OPEN', target_twitter_account='whitehouse',
         # starting_num_tweets=500, contracts=[Contract(ticker_symbol=1117,short_name='54-'),Contract(ticker_symbol=1118,short_name='55 - 58'), Contract(ticker_symbol=1119,short_name='59 - 62')])]
    # mocker.patch.object(
    cid_to_mid = {1111: 1116, 1112: 1116,1113: 1116,1114: 1116, 1117: 1115, 1118: 1115, 1119: 1115}

    predictit.main.tweet_counts={'trump': 800, 'whitehouse': 500}
    # )
    mock_num_trump_tweets = 800
    mock_num_whitehouse_tweets = 500
    mock_num_pence_tweets = 0
    mock_num_potus_tweets = 0
    buy_order_called_states = {1116: [], 1115: []}
    max_buy_orders = 4
    num_buy_orders = 0

    numTrumpTweets = mocker.patch('predictit.api.PredictItAPI.getNumTrumpTweets')
    numTrumpTweets.side_effect = mockNumTrumpTweets
    numPenceTweets = mocker.patch('predictit.api.PredictItAPI.getNumPenceTweets')
    numPenceTweets.side_effect = mockNumPenceTweets
    numWhitehouseTweets = mocker.patch('predictit.api.PredictItAPI.getNumWhitehouseTweets')
    numWhitehouseTweets.side_effect = mockNumWhitehouseTweets
    numPotusTweets = mocker.patch('predictit.api.PredictItAPI.getNumPotusTweets')
    numPotusTweets.side_effect = mockNumPotusTweets

    mock_buy_order_var = mocker.patch('predictit.api.PredictItAPI.buy_order')
    mock_buy_order_var.side_effect = mock_buy_order
    # mock_buy_order_var = mocker.patch('predictit.api.PredictItAPI.buy_order',side_effect=mock_buy_order)

    mock_max_num_shares = mocker.patch('predictit.api.PredictItAPI.max_num_shares_buyable_at_price')
    mock_max_num_shares.side_effect = mock_max_num_shares_buyable_at_price

    api = PredictItAPI(None)

    counter = 0
    while True:
        run_algorithms()
        counter += 1
        if counter == 1000:
            break

    assert num_buy_orders == max_buy_orders
    assert mock_buy_order_var.call_count == max_buy_orders
    # extra 892 at end of list for the short on second highest bucket and long on last bucket
    assert buy_order_called_states[1116] == [884, 888, 892, 892]
    # assert buy_order_called_states[1115] == [555, 559, 563]
    call(1111, False, MAX_NUM_SHARES_TO_BUY, 99) in predictit.api.PredictItAPI.buy_order.calls
    call(1111, False, MAX_NUM_SHARES_TO_BUY, 99) in predictit.api.PredictItAPI.buy_order.calls
    # call(1117, False, MAX_NUM_SHARES_TO_BUY, 99) in predictit.api.PredictItAPI.buy_order.calls
    call(1112, False, MAX_NUM_SHARES_TO_BUY, 99) in predictit.api.PredictItAPI.buy_order.calls
    # call(1118, False, MAX_NUM_SHARES_TO_BUY, 99) in predictit.api.PredictItAPI.buy_order.calls
    call(1113, False, MAX_NUM_SHARES_TO_BUY, 99) in predictit.api.PredictItAPI.buy_order.calls
    # call(1119, False, MAX_NUM_SHARES_TO_BUY, 99) in predictit.api.PredictItAPI.buy_order.calls
    call(1114, True, MAX_NUM_SHARES_TO_BUY, 99) in predictit.api.PredictItAPI.buy_order.calls
    # assert 1 != 1
    # mock_buy_order_var.assert_called_with('whitehouse c4', False, MAX_NUM_SHARES_TO_BUY, 99)

    # assert buy_order_called_state
