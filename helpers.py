import os

from db_torrents_utils import get_torrent_filename, delete_torrent
from main import app


def torrent_full_delete(id_torrent):
    filename = get_torrent_filename(id_torrent)
    if filename:
        file_path = app.config['UPLOAD_FOLDER'] + filename
        if os.path.exists(file_path):
            os.remove(file_path)
            delete_torrent(id_torrent)
