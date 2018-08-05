from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')     # Public config

bootstrap = Bootstrap(app)

from app import views