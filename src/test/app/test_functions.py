import os

def get_logging_config() -> dict[str, any]:
    log_level = 'INFO' if 'prod' == os.environ.get('APP_PROFILE') else 'DEBUG'
    print(f'Log level: {log_level}')
    return {
        'version': 1,
        'formatters': {'simple': {'format': '%(asctime)s %(name)s %(levelname)s %(message)s'}},
        'handlers': {'console': {
            'class': 'logging.StreamHandler', 'level': f'{log_level}', 'formatter': 'simple'}},
        'loggers': {'docchatai.app': {'level': f'{log_level}', 'handlers': ['console'], 'propagate': False}}
    }
