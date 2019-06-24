import logging
import timeit
import sys

logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s - %(message)s',filename='logs-test.txt')
logging.info('starting PredictIt scraper...')

setup="import logging; logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s - %(message)s',filename='logs-test.txt'); logging.info('starting PredictIt scraper...')"

s = """\
logging.info('this is a test run %s: %d' % ('hello', 4))
"""

n = int(sys.argv[1])
time = timeit.timeit(stmt=s, setup=setup, number=n)

print("Average seconds per 100 logs: %0.6f" % (time/n*100))


