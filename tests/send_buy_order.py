from predictit.api import PredictItAPI
from predictit.notifier import PredictItNotifier
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s - %(message)s')

CONTRACT_ID = 14309
IS_YES_ORDER = False
QUANTITY = 1
PRICE = 99

def send_buy_order():
    notifier = PredictItNotifier("alex.wlezien@gmail.com", "houston98", ["a.wlezien@gmail.com", "alex.dai816@gmail.com"])
    api = PredictItAPI(notifier)
    api.create_authed_session('buyaclweed@gmail.com','Houston98')
    api.buy_order(CONTRACT_ID, IS_YES_ORDER, QUANTITY, PRICE)




if __name__ == '__main__':
    send_buy_order()
