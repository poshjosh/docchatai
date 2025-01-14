import logging.config
import os

from app.app import App
from app.config import RunConfig

LOG_LEVEL = 'INFO' if 'prod' == os.environ.get('APP_PROFILE') else 'DEBUG'
logging.config.dictConfig({
    'version': 1,
    'formatters': {'simple': {'format': '%(asctime)s %(name)s %(levelname)s %(message)s'}},
    'handlers': {'console': {
        'class': 'logging.StreamHandler', 'level': f'{LOG_LEVEL}', 'formatter': 'simple'}},
    'loggers': {'app': {'level': f'{LOG_LEVEL}', 'handlers': ['console'], 'propagate': False}}
})

if __name__ == '__main__':
    try :
        App.run(RunConfig())
    finally:
        App.shutdown()