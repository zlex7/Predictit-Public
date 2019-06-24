
class Market(object):
    def __init__(self, ticker_symbol=None, long_name=None, short_name=None, image_url=None, url=None, status=None, contracts=None):
        self.ticker_symbol = int(ticker_symbol)
        self.long_name = str(long_name)
        self.short_name = str(short_name)
        self.image_url = image_url
        self.url = url
        # print('contracts = %s ' %contracts)
        # print('setting contracts to %s' % contracts)
        if contracts is None:
            self.contracts = []
        else:
            self.contracts = contracts
        self.status = status

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__



class Contract(object):
    def __init__(self, ticker_symbol=None, long_name=None, short_name=None, time_end=None, image_url=None, status=None, min_tweets=-1000000000, max_tweets=1000000000):
        self.ticker_symbol = int(ticker_symbol)
        self.long_name = str(long_name)
        self.short_name = str(short_name)
        self.time_end = time_end
        self.image_url = image_url
        self.status = status
        self.min_tweets = int(min_tweets)
        self.max_tweets = int(max_tweets)

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__



class ContractInfo(object):
    def __init__(self, ticker_symbol=None, timestamp_as_date=None, timestamp=-1.0, best_buy_yes_cost=-1, best_buy_no_cost=-1, best_sell_yes_cost=-1,
                        best_sell_no_cost=-1, last_trade_price=-1, last_close_price=-1, todays_volume=-1, shares_traded=-1,
                        total_shares=-1, todays_change=-1):
        self.ticker_symbol = int(ticker_symbol)
        self.timestamp = float(timestamp)
        self.timestamp_as_date = timestamp_as_date
        self.best_buy_yes_cost = int(best_buy_yes_cost)
        self.best_buy_no_cost = int(best_buy_no_cost)
        self.best_sell_yes_cost = int(best_sell_yes_cost)
        self.best_sell_no_cost = int(best_sell_no_cost)
        self.last_trade_price = int(last_trade_price)
        self.last_close_price = int(last_close_price)
        self.todays_volume = int(todays_volume)
        self.shares_traded = int(shares_traded)
        self.total_shares = int(total_shares)
        self.todays_change = int(todays_change)

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class MarketVolumeData(object):
    def __init__(self, ticker_symbol, timestamp, contract_volumes):
        self.ticker_symbol = ticker_symbol
        self.timestamp = timestamp
        self.contract_volumes = contract_volumes

# Doesn't make sense to have a contractvlumedata class if a market_volume_data field
# will only have 1 thing in it. 
class ContractVolumeData(object):
    def __init__(self, ticker_symbol, timestamp, trade_volume, contract_name, contract_id):
        self.ticker_symbol = ticker_symbol
        self.timestamp = timestamp
        self.trade_volume = trade_volume
        self.contract_name = contract_name

    def __str__(self):
        return self.contract_name + ":" + str(self.trade_volume)


class Order(object):
    def __init__(self, ticker_symbol, is_yes_order, price, quantity):
        self.ticker_symbol = ticker_symbol
        self.is_yes_order = is_yes_order
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return  str(self.price) + ":" + str(self.quantity)

class ContractOrderBook(object):
    def __init__(self, ticker_symbol, short_name, timestamp, yes_orders, no_orders):
        self.ticker_symbol = ticker_symbol
        self.short_name = short_name
        self.timestamp = timestamp
        self.yes_orders = yes_orders
        self.no_orders = no_orders

class TwitterMarket(Market):
    def __init__(self, ticker_symbol=None, long_name=None, short_name=None, image_url=None, url=None, status=None, contracts=None, starting_num_tweets=-1, target_twitter_account=None, keyword=None):
        # keyword='')
        # start_time=None, end_time=None):
        # self.start_time = float(start_time)
        # self.end_time = float(end_time)
        # self.keyword = keyword
        self.starting_num_tweets = int(starting_num_tweets)
        self.target_twitter_account = target_twitter_account
        self.keyword = keyword
        self.is_keyword_market = keyword is not None
        super(TwitterMarket, self).__init__(ticker_symbol=ticker_symbol, long_name=long_name, short_name=short_name, image_url=image_url,
                                        url=url, status=status, contracts=contracts)
