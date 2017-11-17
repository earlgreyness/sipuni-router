from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babelex import Babel

from router.utils import configure_logging

app = Flask(__name__)
app.config.from_object('router.config')
configure_logging(app)
db = SQLAlchemy(app)
babel = Babel(app)  # for admin localization

import router.models
import router.views.auth
import router.views.webhook
import router.views.admin
