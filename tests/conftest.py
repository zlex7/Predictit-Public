import pytest
import logging
import sys
from predictit.db import *



@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    print('running logging')
    logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s - %(message)s')
    logging.info('after basicConfig()')

@pytest.fixture(scope="session")
def db():
    r = RedisPredictItDb('0.0.0.0', 6379)
    r.conn.flushdb()
    yield r
    r.conn.flushdb()
