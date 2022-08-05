# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from session import ItsdangerousSessionInterface
from pg_config import DB_URI

####### Uncomment this for use Mysql/MariaDB ########
#from mysql_config import DB_URI

app = Flask(__name__)

####### Edit this options ###########################
TORRENT_PERSIST = False
UPLOAD_FOLDER = '/path/to/torrents/folder/'
PASSWORD_SALT = 'your_salt_for_password'
SESSION_SALT = 'your_salt_for_session'
PAGE_TORRENT_COUNT = 20
APP_HOST = '127.0.0.1'
APP_PORT = 8080
app.secret_key = 'your_secret_app_key'
#####################################################

ALLOWED_EXTENSIONS = {'torrent'}
TORRENTS_STAT_ROW_ID = 1

app.config['DEBUG'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_NATIVE_UNICODE'] = True
db = SQLAlchemy(app, False)

app.session_interface = ItsdangerousSessionInterface()
app.session_interface.salt = SESSION_SALT
