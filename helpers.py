import os

from db_torrents_utils import get_torrent_filename, delete_torrent, add_torrent
from main import app
from torrent_utils import decode
from utils import uniqid


def upload_torrent_file(name, description, file_context, filename, user_id):
    if name != "" and description and filename != "":
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            uid = uniqid()
            filename = "".join([uid, ".torrent"])
            file_context.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            try:
                torrent_file = app.config['UPLOAD_FOLDER'] + filename
                if torrent_file:
                    torrent_ = decode(torrent_file)
                    size = 0
                    try:
                        info = torrent_["info"]["files"]
                        for file_context in info:
                            size = size + file_context["length"]
                    except KeyError:
                        size = torrent_["info"]["length"]
                    size = round((size * 0.001) * 0.001, 2)
                    add_torrent(name, description, filename, user_id, size)
            except IOError:
                return


def torrent_full_delete(id_torrent):
    filename = get_torrent_filename(id_torrent)
    if filename:
        file_path = app.config['UPLOAD_FOLDER'] + filename
        if os.path.exists(file_path):
            os.remove(file_path)
            delete_torrent(id_torrent)
