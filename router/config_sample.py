import os.path as op
import json

import arrow


class ArrowJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, arrow.Arrow):
            return str(obj)
        return super().default(obj)


# flask
SECRET_KEY = ''

# flask-sqlalchemy
SQLALCHEMY_DATABASE_URI = 'postgresql://router:@localhost:5432/router'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# flask-restful
ERROR_404_HELP = False
RESTFUL_JSON = dict(
    ensure_ascii=False,
    sort_keys=True,
    indent=4,
    cls=ArrowJSONEncoder,
)

# flask-babelex
BABEL_DEFAULT_LOCALE = 'ru'

# flask-cors
CORS_HEADERS = 'Content-Type'

# custom
ADMIN_PASSWORD = ''
PROJECT_ROOT = op.dirname(op.realpath(__file__))
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] [%(levelname).1s] (%(module)s:%(lineno)d) %(message)s',
        },
    },
    'handlers': {
        'rotated': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': op.normpath(op.join(PROJECT_ROOT, '..', 'logs', 'app.log')),
            'maxBytes': 10 * 1024000,
            'backupCount': 2,
            'encoding': 'utf-8',
            'formatter': 'default',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'router': {
            'level': 'DEBUG',
            'handlers': ['rotated'],
        },
    },
}
