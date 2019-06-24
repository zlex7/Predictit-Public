import pytest
from predictit.models import *
import time

def test_db(db):
    pass
    # db.delete_all_contracts()
    # contracts = db.get_all_contracts()
    # print(contracts)
    # db.put_contract(Contract('ABC','ABCDEFG','ABCDE',1000,"www.google.com",['rule1','rule2']))
    # print(db.get_contract('ABC'))
    # print(db.get_all_contracts())
    # t = int(time.time())
    # contract_info_list = [ContractInfo(t + i,90,10,10,90,80,1000,5000,100000,10) for i in range(5)]
    # db.put_all_contracts_info('ABC',contract_info_list)
    # print(db.get_all_contracts_info())
    # print (db.get_contract('ABCD'))

def test_put_and_get_empty_market(db):
    market = Market(ticker_symbol=1111, long_name='test long name', short_name='test short name',
                        image_url='test image url', url='test url', status='test status')
    db.put_market(market)
    m = db.get_market(market.ticker_symbol)
    assert m == market

def test_put_market_with_one_contract(db):
    market = Market(ticker_symbol=1222, long_name='test long name', short_name='test short name',
                        image_url='test image url', url='test url', status='test status')
    market.contracts.append(Contract(ticker_symbol=2111, long_name='test long name', short_name='test short name',
                        time_end='N/A', image_url='test image url', status='test status'))
    db.put_market(market)
    # print('%s' % db.get_all_contracts_for_market(market.ticker_symbol)[0])
    # print('%s' % market.contracts[0])
    # print(value = { k : market.contracts[k] for k in set(market.contracts) - set( db.get_all_contracts_for_market(market.ticker_symbol)[0]) })
    assert db.get_all_contracts_for_market(market.ticker_symbol)[0] == market.contracts[0]
    assert db.get_all_contracts_for_market(market.ticker_symbol) == market.contracts
    assert db.get_market(market.ticker_symbol) == market

def test_put_market_with_multiple_contracts(db):
    market = Market(ticker_symbol=1333, long_name='test long name', short_name='test short name',
                        image_url='test image url', url='test url', status='test status')
    market.contracts.append(Contract(ticker_symbol=2222, long_name='test long name', short_name='test short name',
                        time_end='N/A', image_url='test image url', status='test status'))
    market.contracts.append(Contract(ticker_symbol=2333, long_name='test long name', short_name='test short name',
                        time_end='N/A', image_url='test image url', status='test status'))
    db.put_market(market)

    assert sorted(db.get_all_contracts_for_market(market.ticker_symbol), key=lambda x: x.ticker_symbol) == sorted(market.contracts,key=lambda x: x.ticker_symbol)
    m = db.get_market(market.ticker_symbol)
    m.contracts.sort(key=lambda x: x.ticker_symbol)
    market.contracts.sort(key=lambda x: x.ticker_symbol)
    assert m == market

def test_put_contract_info(db):
    market = Market(ticker_symbol=1444, long_name='test long name', short_name='test short name',
                        image_url='test image url', url='test url', status='test status')
    market.contracts.append(Contract(ticker_symbol=2444, long_name='test long name', short_name='test short name',
                        time_end='N/A', image_url='test image url', status='test status'))
    db.put_market(market)
    contract_info_test = ContractInfo(ticker_symbol=market.contracts[0].ticker_symbol, timestamp_as_date='N/A', timestamp=time.time(), best_buy_yes_cost=1, best_buy_no_cost=2,
                        best_sell_yes_cost=3, best_sell_no_cost=4, last_trade_price=5, last_close_price=6, todays_volume=7)
    db.put_contract_info(contract_info_test)
    assert db.get_contract_info(market.contracts[0].ticker_symbol) == [contract_info_test]

def test_put_multiple_contract_info(db):
    market = Market(ticker_symbol=1555, long_name='test long name', short_name='test short name',
                        image_url='test image url', url='test url', status='test status')
    market.contracts.append(Contract(ticker_symbol=2555, long_name='test long name', short_name='test short name',
                        time_end='N/A', image_url='test image url', status='test status'))
    db.put_market(market)
    contract_info_test = [ContractInfo(ticker_symbol=market.contracts[0].ticker_symbol, timestamp_as_date='N/A', timestamp=time.time(), best_buy_yes_cost=1, best_buy_no_cost=2,
                        best_sell_yes_cost=3, best_sell_no_cost=4, last_trade_price=5, last_close_price=6, todays_volume=7), ContractInfo(ticker_symbol=market.contracts[0].ticker_symbol, timestamp_as_date='N/A', timestamp=time.time(), best_buy_yes_cost=1, best_buy_no_cost=2,
                                            best_sell_yes_cost=3, best_sell_no_cost=4, last_trade_price=5, last_close_price=6, todays_volume=7)]
    db.put_multiple_contracts_info(contract_info_test)
    assert db.get_contract_info(market.contracts[0].ticker_symbol) == contract_info_test
