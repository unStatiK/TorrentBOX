# -*- coding: utf-8 -*-

from main import ALLOWED_EXTENSIONS
import torrent_parser as tp


def decode(torrent_file):
    return tp.parse_torrent_file(torrent_file)


def decode_data(torrent_data):
    return tp.decode(torrent_data, errors="ignore")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
