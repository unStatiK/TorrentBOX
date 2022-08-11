# -*- coding: utf-8 -*-

import os
import base64

from db_torrents_utils import *
from main import app, TORRENT_PERSIST
from torrent_utils import decode, decode_data
from utils import uniqid


def upload_torrent_file(name, description, file_context, filename, user_id):
    if name != "" and description and filename != "":
        uid = uniqid()
        filename = "".join([uid, ".torrent"])
        if TORRENT_PERSIST:
            torrent_ = decode_data(file_context.read())
            size = get_torrent_size(torrent_)
            file_context.seek(0)
            file_payload = base64.b64encode(file_context.read())
            new_id = add_torrent_with_payload(name, description, filename, user_id, size, file_payload.decode("utf-8"))
            store_files_and_size(torrent_, new_id, size)
        else:
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                file_context.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                try:
                    torrent_file = app.config['UPLOAD_FOLDER'] + filename
                    if torrent_file:
                        torrent_ = decode(torrent_file)
                        size = get_torrent_size(torrent_)
                        new_id = add_torrent(name, description, filename, user_id, size)
                        store_files_and_size(torrent_, new_id, size)
                except IOError:
                    return


def store_files_and_size(torrent, torrent_id, size):
    files = []
    if 'files' in torrent["info"]:
        info = torrent["info"]["files"]
        for file in info:
            files.append("/".join(file['path']))
    else:
        info = torrent
        files.append(info['info']['name'])
    if files:
        add_torrent_files_and_size(files, torrent_id, size)


def get_torrent_size(torrent_dict):
    size = 0
    try:
        info = torrent_dict["info"]["files"]
        for file_context in info:
            # length in bytes
            size = size + file_context["length"]
    except KeyError:
        # length in bytes
        size = torrent_dict["info"]["length"]
    return size


def torrent_full_delete(id_torrent):
    filename = get_torrent_filename(id_torrent)
    if filename:
        if not TORRENT_PERSIST:
            file_path = app.config['UPLOAD_FOLDER'] + filename
            if os.path.exists(file_path):
                os.remove(file_path)
        delete_torrent(id_torrent)
