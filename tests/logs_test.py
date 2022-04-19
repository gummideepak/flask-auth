"""This test the homepage"""
import logging
from os.path import exists

log = logging.getLogger("myApp")

def test_logging(client):
    """This makes the index page"""
    log.info('test')
    assert exists('app/logs/myapp.log')
