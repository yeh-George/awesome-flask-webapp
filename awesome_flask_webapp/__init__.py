import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from awesome_flask_webapp.settings import config

app = Flask('awesome_flask_webapp')
config_name = os.getenv('FLASK_CONFIG', 'developement')
app.config.from_object(config[config_name])

@app.route('/')
def index():
    return '<h1>hello, awesome_flask_webapp</h1>'

