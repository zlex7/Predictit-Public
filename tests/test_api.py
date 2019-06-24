import pytest
import datetime
import dateutil
import pytz
from predictit.api import PredictItAPI
from predictit.models import ContractInfo
import predictit
@pytest.mark.parametrize("mock_json,expected", [
    ([
        [{
            'contracts': [{
                'id': 1234,
                'bestBuyYesCost': '.20',
                'bestBuyNoCost': '.80',
                'bestSellYesCost': '.19',
                'bestSellNoCost': '.79',
                'lastTradePrice': '.19',
                'lastClosePrice': '.15'
            }],
            'timeStamp': '2019-01-18T17:10:49.989945'
        }], [ContractInfo(ticker_symbol=1234, best_buy_yes_cost='20',
            best_buy_no_cost='80',  best_sell_yes_cost='19',
            best_sell_no_cost='79', last_trade_price='19',
            last_close_price='15', timestamp=pytz.timezone('US/Eastern').normalize(pytz.timezone('US/Eastern').localize(dateutil.parser.parse('2019-01-18T17:10:49.989945'))).timestamp(),
            timestamp_as_date=pytz.timezone('US/Eastern').normalize(pytz.timezone('US/Eastern').localize(dateutil.parser.parse('2019-01-18T17:10:49.989945'))))]
    ])
])
def test_get_current_contracts_info(mocker, mock_json, expected):
    mock_json_function = mocker.patch('predictit.api.PredictItAPI.getJSON')
    mock_json_function.return_value = mock_json
    api = PredictItAPI(None)
    assert api.getCurrentContractsInfo() == expected

def test_get_num_tweets_generic(mocker):
    # mock_json_function = mocker.patch('predictit.api.PredictItAPI.getJSON')
    mock_requests_get = mocker.patch('requests.get')
    mocker.spy(predictit.notifier.PredictItNotifier, 'send_notification')
    # mock_json_function.return_value = mock_json
    api = PredictItAPI(None)
    # assert api.getCurrentContractsInfo() == expected
