import logging.config
from collections import OrderedDict
from functools import wraps

from flask_restful import output_json, Api


def configure_logging(app):
    # Triggers removing existing handlers when accessed first time:
    app.logger
    logging.config.dictConfig(app.config['LOGGING'])


class UnicodeApi(Api):
    def __init__(self, *args, **kwargs):
        """
        Unicode in Google Chrome now handled correctly for JSONs
        https://github.com/flask-restful/flask-restful/issues/552
        """
        super().__init__(*args, **kwargs)
        self.representations = OrderedDict(
            [('application/json; charset=utf-8', output_json)]
        )


def context(f):
    from router import app

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            with app.app_context():
                return f(*args, **kwargs)
        except Exception:
            app.logger.exception('')

    return decorated
