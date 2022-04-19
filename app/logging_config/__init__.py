import logging
import datetime
import time
from logging.config import dictConfig

import flask
from flask import request, current_app, g
from rfc3339 import rfc3339

from app.logging_config.formatter import RequestFormatter

logging_blueprint = flask.Blueprint('logging_blueprint', __name__)

@logging_blueprint.before_app_request
def before_request():
    g.start = time.time()
    # current_app.logger.info("Before Request")
    # log = logging.getLogger("myApp")
    # log.info("My App Logger")

@logging_blueprint.after_app_request
def after_request(response):
    if request.path == '/favicon.ico':
        return response
    elif request.path.startswith('/static'):
        return response
    elif request.path.startswith('/bootstrap'):
        return response
    now = time.time()
    duration = round(now - g.start, 2)
    dt = datetime.datetime.fromtimestamp(now)
    timestamp = rfc3339(dt, utc=True)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    host = request.host.split(':', 1)[0]
    args = dict(request.args)
    log_params = [
        ('method', request.method),
        ('path', request.path),
        ('status', response.status_code),
        ('duration', duration),
        ('time', timestamp),
        ('ip', ip),
        ('host', host),
        ('params', args)
    ]
    request_id = request.headers.get('X-Request-ID')
    if request_id:
        log_params.append(('request_id', request_id))
    parts = []
    for name, value in log_params:
        part = name + ': ' + str(value) + ', '
        parts.append(part)
    line = " ".join(parts)
    #this triggers a log entry to be created with whatever is in the line variable
    # app.logger.info('this is the plain message')
    return response

@logging_blueprint.before_app_first_request
def configure_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
    # log = logging.getLogger("myApp")
    # log.info("My App Logger")
    # log = logging.getLogger("myerrors")
    # log.info("THis broke")

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'RequestFormatter': {
            '()': 'app.logging_config.formatter.RequestFormatter',
            'format': '[%(asctime)s] [%(process)d] %(remote_addr)s requested %(url)s'
                        '%(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'file.handler.myapp': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'app/logs/myapp.log',
            'maxBytes': 10000000,
            'backupCount': 5,
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default','default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'myApp': {  # if __name__ == '__main__'
            'handlers': ['file.handler.myapp'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}
