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

    def get_contract_info_set_name(self, contract_ticker_symbol):
        pass

    def put_contract(self, contract):
        pass

    def get_contract(self, contract_ticker_symbol):
        pass

    def get_all_contracts(self):
        pass

    def delete_contracts(self, symbols_to_delete):
        pass

    def delete_all_contracts(self):
        pass

    def put_contract_info(self, contract_ticker_symbol, contract_info):
        pass

    def put_multiple_contracts_info(self, contract_ticker_symbol, contract_info_points):
        pass

    def get_contract_info(self, contract_ticker_symbol, hours=0, minutes=15, seconds=0, start_time=None):
        pass

    def get_all_contracts_info(self, hours=0, minutes=15, seconds=0, start_time=None):
        pass



class RedisPredictItDb(PredictItDb):

    def __init__(self, db_host, db_port):
        self.conn = redis.StrictRedis(host=db_host, port=db_port, db=0, decode_responses=True)
        self.contract_info_set_name_suffix = "_time_series"
        self.contracts_set_name = "contracts"
        self.markets_set_name = "markets"
        self.twitter_markets_set_name = "twitter_markets"

    def get_contract_info_set_name(self, contract_ticker_symbol):
        return contract_ticker_symbol + self.contract_info_set_name_suffix

    def get_all_twitter_markets(self):
        try:
            markets = []
            market_names = self.conn.smembers(self.twitter_markets_set_name)
            print('current market names = %s' % market_names)
            for mn in market_names:
                ticker = self.conn.hget(mn, 'ticker_symbol')
                markets.append(self.get_market(ticker))
            return markets
        except Exception as e:
            print(traceback.format_exc())
            return False

    def put_all_markets(self, markets):
        print('putting markets')
        try:
            p = self.conn.pipeline()
            for market in markets:
                # for /tmgf in twitter_market_given_info:

                market_key_name = 'market_%s' % market.ticker_symbol
                contracts_set_key_name = '%s_contracts' % market_key_name
                market_values = vars(market)
                p.hmset(market_key_name, {k:market_values[k] for k in market_values if k != 'contracts'})
                print(vars(market))
                for c in market.contracts:
                    contract_key_name = 'contract_%s' % c.ticker_symbol
                    p.sadd(contracts_set_key_name, contract_key_name)
                    p.hmset(contract_key_name, vars(c))
                p.sadd(self.markets_set_name, market_key_name)
                if isinstance(market, TwitterMarket):
                    p.sadd(self.twitter_markets_set_name, market_key_name)
            r = p.execute()
            print('r = %s' % r)
            return r
        except Exception as e:
            print(traceback.format_exc())
            return False

    def put_market(self, market):
        self.put_all_markets([market])

    def get_market(self, market_ticker_symbol):
        try:
            market_key_name = 'market_%s' % market_ticker_symbol
            print(market_key_name)
            r = self.conn.hgetall(market_key_name)
            m = None
            is_twitter_market = self.conn.sismember(self.twitter_markets_set_name, market_key_name)
            if is_twitter_market:
                m = TwitterMarket(**r)
            else:
                m = Market(**r)
            m.contracts = self.get_all_contracts_for_market(m.ticker_symbol)
            print(r)
            return m
        except Exception as e:
            print(traceback.format_exc())
            return False

    # def get_twitter_market(self, market_ticker_symbol):
    #     try:
    #         market_key_name = 'market_%s' % market_ticker_symbol
    #         r = self.conn.hgetall(market_key_name)
    #         m = TwitterMarket(**r)
    #         m.contracts = self.get_all_contracts_for_market(m.ticker_symbol)
    #         print(r)
    #         return m
    #     except Exception as e:
    #         print(traceback.format_exc())
    #         return False

    def get_all_markets(self):
        try:
            markets = []
            market_names = self.conn.smembers(self.markets_set_name)
            print('current market names = %s' % market_names)
            for mn in market_names:
                ticker = self.conn.hget(mn, 'ticker_symbol')
                markets.append(self.get_market(ticker))
            return markets
        except Exception as e:
            print(traceback.format_exc())
            return False

    # def put_all_contracts(self, contracts):
    #     try:
    #         p = self.conn.pipeline()
    #         for c in contracts:
    #             contract_key_name = 'contract_%s' % c.ticker_symbol
    #             p.sadd(contracts_set_key_name, contract_key_name)
    #             p.hmset(contract_key_name, vars(c))
    #         r = p.execute()
    #         print(r)
    #         return r
    #     except Exception as e:
    #         print(traceback.format_exc())
    #         return False
    #
    # def put_contract(self, contract):
    #     self.put_all_contracts([contract])

    def get_contract(self, contract_ticker_symbol):
        try:
            r = self.conn.hgetall('contract_%s' % contract_ticker_symbol)
            print(r)
            return Contract(**r[0])
        except Exception as e:
            print(traceback.format_exc())
            return False

    def get_all_contracts_for_market(self, market_ticker_symbol):
        try:
            contracts_set_name = 'market_%s_contracts' % market_ticker_symbol
            contract_names = self.conn.smembers(contracts_set_name)
            p = self.conn.pipeline()
            for cn in contract_names:
                p.hgetall(cn)
            r = p.execute()
            print ('r = %s' % r)
            contracts = [Contract(**dct) for dct in r if dct]
            return contracts
        except Exception as e:
            print(traceback.format_exc())
            return None


    def delete_markets(self, market_tickers):
        try:
            p = self.conn.pipeline()
            for mt in market_tickers:
                p.delete('market_%s' % mt)
                p.srem(self.markets_set_name, mt)
                contracts_set_name = 'market_%s_contracts' % mt
                contract_names = self.conn.smembers(contracts_set_name)
                for cn in contract_names:
                    for info_point_key in self.conn.zrange(self.get_contract_info_set_name(cn), 0, -1):
                        p.delete(info_point_key)
                    p.delete(self.get_contract_info_set_name(cn))
                p.delete(contracts_set_name)
            r = p.execute()
            print(r)
            return r
        except Exception as e:
            print(traceback.format_exc())
            return False

    def put_contract_info(self, contract_info):
        self.put_multiple_contracts_info([contract_info])

    def put_multiple_contracts_info(self, contract_info_points):
        p = self.conn.pipeline(transaction=True)
        for info_point in contract_info_points:
            contract_key = 'contract_%s' % info_point.ticker_symbol
            info_point_key = contract_key + ':' + str(info_point.timestamp)
            p.hmset(info_point_key, vars(info_point))
            p.zadd(self.get_contract_info_set_name(contract_key), {info_point_key: info_point.timestamp})
        results = p.execute()
        return results

    def get_contract_info(self, contract_ticker_symbol, hours=0, minutes=15, seconds=0, start_time=None):
        contract_key = 'contract_%s' % contract_ticker_symbol
        time_interval = hours * 3600 + minutes * 60 + seconds
        if start_time is None:
            start_time = int(time.time() - time_interval)
        print("start_time = %s" % start_time)
        p = self.conn.pipeline(transaction=False)
        p.zrangebyscore(self.get_contract_info_set_name(contract_key), str(start_time), '+inf')
        info_point_keys = p.execute()
        print ("info_point_keys = %s" % info_point_keys)
        for key in info_point_keys[0]:
            p.hgetall(key)
        results = [ContractInfo(**dct) for dct in p.execute()]
        return results

    def get_all_contracts_info(self, hours=0, minutes=15, seconds=0, start_time=None):
        results = {}
        for contract_ticker_symbol in self.get_all_contract_ticker_symbols():
            print("getting info points for '%s'" % contract_key)
            results[contract_ticker_symbol] = self.get_contract_info(contract_ticker_symbol,hours=hours,minutes=minutes,seconds=seconds,start_time=start_time)
        return results
