# -*- coding: utf-8 -*-

import base64

from main import app, TORRENT_PERSIST
from db_torrents_utils import get_torrent_by_id, get_torrent_payload

def get_torrent_data(torrent_id):
    torrent = get_torrent_by_id(torrent_id)
    if torrent:
        if TORRENT_PERSIST == True:
            payload = get_torrent_payload(torrent_id)
            return base64.b64decode(payload.payload.encode())
        else:
            torrent_filename = app.config['UPLOAD_FOLDER'] + torrent.filename
            if os.path.exists(torrent_filename):
                torrent_file = open(torrent_filename, "rb")
                torrent_data = torrent_file.read()
                in_file.close()
                return torrent_data
