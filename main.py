# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from session import ItsdangerousSessionInterface
from pg_config import DB_URI

# Uncomment this for use Mysql/MariaDB ########
# from mysql_config import DB_URI

app = Flask(__name__)
babel = Babel(app)

# Edit this options #
TORRENT_PERSIST = False  # store torrent data in db
'''
generate direct link for download .torrent file:
APP_HOST/UPLOAD_FOLDER/file.torrent
'''
DIRECT_TORRENT_LINK = False
UPLOAD_FOLDER = '/full_path/to/static/folder/'
PASSWORD_SALT = 'your_salt_for_password'
SESSION_SALT = 'your_salt_for_session'
PAGE_TORRENT_COUNT = 20
APP_HOST = '127.0.0.1'
APP_PORT = 8080
LOCALE = 'auto'  # 'en', 'ru' or auto
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
app.config['LANGUAGES'] = ['en', 'ru']
db = SQLAlchemy(app, False)

app.session_interface = ItsdangerousSessionInterface()
app.session_interface.salt = SESSION_SALT
