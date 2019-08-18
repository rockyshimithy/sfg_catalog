import logging.config  # noqa
import pathlib

MOTOR_DB = 'sfg_catalog'
MOTOR_URI = 'mongodb://127.0.0.1:27017/sfg_catalog'
MOTOR_MAX_POOL_SIZE = 1

BASE_DIR = pathlib.Path(__file__).parent.parent
TEMPLATES_DIR = str(BASE_DIR / 'sfg_catalog' / 'templates')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(process)d] [%(levelname)s] %(name)s:%(lineno)d - %(message)s'  # noqa
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'info_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'verbose',
            'filename': 'info.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB,
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'verbose',
            'filename': 'errors.log',
            'maxBytes':  10 * 1024 * 1024,  # 10 MB,
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'asyncio': {
            'level': 'CRITICAL',
            'propagate': True,
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'info_file_handler', 'error_file_handler']
    }
}
