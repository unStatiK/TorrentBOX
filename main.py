# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from session import ItsdangerousSessionInterface

app = Flask(__name__)

# UPLOAD_FOLDER = '/path/to/torrents/folder/'
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = {'torrent'}
SALT_PASS = "your_salt_for_password"
PAGE_TORRENT_COUNT = 20

app.secret_key = 'your_secret_app_key'

#app.config['DEBUG'] = False
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://user:password@host/db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:117@127.0.0.1/box'
db = SQLAlchemy(app, False)

app.session_interface = ItsdangerousSessionInterface()
