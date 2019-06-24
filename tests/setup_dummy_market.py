import pytest
import datetime
import dateutil
import pytz
import predictit.api
from predictit.models import TwitterMarket, Contract
import predictit.main
import os
# import mock
from unittest.mock import patch

def fakeGetRunningMarkets(twitter_markets_given_info):
    markets = []
    # print(twitter_markets_given_info)
    for tmgf in twitter_markets_given_info:
        tm = TwitterMarket(ticker_symbol=1111, long_name='this is a fake market yo', short_name='fake market yo',
                image_url='', url='url', status='open', target_twitter_account=tmgf[1],
                 starting_num_tweets=tmgf[2],keyword=tmgf[3] if 'keyword' in tmgf[1] else None)
        is_keyword_market = 'keyword' in tmgf[1]
        contracts = [Contract(ticker_symbol=0, long_name='this is a fake contract for %s 1' % tm.target_twitter_account,
                                 short_name='0' if is_keyword_market else '0-',
                                 time_end='N/A',
                                 image_url='', status='open')]
        for i in range(1,5):
            contracts.append(Contract(ticker_symbol=i, long_name='this is a fake contract for %s %d' % (tm.target_twitter_account,i),
                                     short_name=str(i) if is_keyword_market else '%d-%d' % ((i - 1) * 5 + 1,(i)*5),
                                     time_end='N/A',
                                     image_url='', status='open'))
        contracts.append(Contract(ticker_symbol=5, long_name='this is a fake contract for %s %d' % (tm.target_twitter_account,5),
                                 short_name=str(5) if is_keyword_market else '%d+' % (4 * 5 + 1),
                                 time_end='N/A',
                                 image_url='', status='open'))
        tm.contracts = contracts
        markets.append(tm)
    return markets

@patch('predictit.api.PredictItAPI.getRunningMarkets')
def setup_dummy_market(MockGetRunningMarkets):
    MockGetRunningMarkets.side_effect = fakeGetRunningMarkets
    # os.system('main.py')
    predictit.main.main()

def test_get_num_tweets_generic(mocker):
    # mock_json_function = mocker.patch('predictit.api.PredictItAPI.getJSON')
    mock_requests_get = mocker.patch('requests.get')
    mocker.spy(predictit.notifier.PredictItNotifier, 'send_notification')
    # mock_json_function.return_value = mock_json
    api = PredictItAPI(None)
    # assert api.getCurrentContractsInfo() == expected

if __name__ == '__main__':
    setup_dummy_market()
