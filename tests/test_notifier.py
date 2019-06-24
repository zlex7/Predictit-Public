from predictit.notifier import *
from predictit.models import *


def test_notifier():
  LAST_EMAIL_EXCEPTION_TIME = -100
  LAST_EMAIL_503_TIME = -100
  EMAIL_INTERVAL = 60
  REQUEST_WAIT_TIME = 0

  notifier = PredictItNotifier("alex.wlezien@gmail.com", "houston98", ["a.wlezien@gmail.com", "alex.dai186@gmail.com"])

  try:
    assert False
  except Exception as e:
    traceback_str = ''.join(traceback.format_tb(e.__traceback__))
    curr_time = time.time()
    if curr_time - LAST_EMAIL_EXCEPTION_TIME > EMAIL_INTERVAL:
       LAST_EMAIL_EXCEPTION_TIME = curr_time
       notifier.send_notification('%s: Requests Error when pinging.' % curr_time, traceback_str)
    time.sleep(REQUEST_WAIT_TIME)

if __name__ == "__main__":
  test_notifier()