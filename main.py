# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from session import ItsdangerousSessionInterface

app = Flask(__name__)

####### Edit this options ###########################
UPLOAD_FOLDER = '/path/to/torrents/folder/'
PASSWORD_SALT = 'your_salt_for_password'
SESSION_SALT = 'your_salt_for_session'
PAGE_TORRENT_COUNT = 20
APP_HOST = '127.0.0.1'
APP_PORT = 8080
app.secret_key = 'your_secret_app_key'
#####################################################

ALLOWED_EXTENSIONS = {'torrent'}

app.config['DEBUG'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://user:password@host/db'
db = SQLAlchemy(app, False)

app.session_interface = ItsdangerousSessionInterface()
