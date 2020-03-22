from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask('awesome_flask_webapp')

@app.route('/')
def index():
    return '<h1>hello, awesome_flask_webapp</h1>'

