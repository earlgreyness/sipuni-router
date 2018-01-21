from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from router.utils import configure_logging

app = Flask(__name__)
app.config.from_object('router.config')
configure_logging(app)
db = SQLAlchemy(app)

import router.models
import router.views
