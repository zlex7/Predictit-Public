class Algorithm(object):

    def __init__(self):
        pass

    def update():
        # 1. read data from database.
        # 2. Run logic/model on data.
        # 3. Execute a trade if needed.
        pass


class VolatilityAlgorithm(Algorithm):

    def update():
        pass

    def get_volatile_contracts(self):
        current_contracts = db.get_all_contracts()
        volatile_contracts = []
        for contract in current_contracts:
            contract_info_series = ContractInfoTimeSeries(db.get_contract_info(contract.ticker_symbol))
            print("collected %d data points about %s" % (len(contract_info_series), contract.ticker_symbol))
            perct_chng = contract_info_series.get_percentage_change_from_start_to_end()
            if abs(perct_chng) > VOLATILITY_PERCENTAGE_THRESHOLD:
                volatile_contracts.append(contract)
                # if (contract_info_series.is_volatile_simple())

    def monitor_contracts(self):
        while True:
            contracts = get_volatile_contracts()
            for contract in contracts:
                # second argument is a placeholder
                notifier.send_notification(contract, 0)
            time.sleep(5)
