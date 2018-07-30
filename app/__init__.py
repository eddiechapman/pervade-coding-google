from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')     # Public config
app.config.from_pyfile('config.py')  # Instance folder config

from app import routes