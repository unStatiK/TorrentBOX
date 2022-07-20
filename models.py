# -*- coding: utf-8 -*-

from main import db
from sqlalchemy.orm import relationship

tags_links = db.Table('tags_links', db.metadata,
                      db.Column('id_tags', db.Integer, db.ForeignKey('tags.id')),
                      db.Column('id_torrent', db.Integer, db.ForeignKey('torrents.id'))
                      )


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)

    def __init__(self, name):
        self.name = name


class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    status = db.Column(db.Integer)

    def __init__(self, name, password, status):
        self.name = name
        self.password = password
        self.status = status


class Torrents(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    filename = db.Column(db.String(255))
    id_acc = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    size = db.Column(db.Float)
    tags_ = relationship("Tags", secondary=tags_links)

    def __init__(self, name, description, filename, id_acc, size):
        self.name = name
        self.description = description
        self.filename = filename
        self.id_acc = id_acc
        self.size = size

    @staticmethod
    def _find_tag(id_torrent):
        tags = Tags.query.filter_by(id=id_torrent)
        tag = tags.first()
        return tag

    def _get_tags(self):
        return [x.id for x in self.tags_]

    def _set_tags(self, value):
        for id_torrent in value:
            self.tags_.append(self._find_tag(id_torrent))

    str_tags = property(_get_tags, _set_tags)


class TorrentsData(db.Model):
    id_torrent = db.Column(db.Integer, db.ForeignKey('torrents.id'), primary_key=True, autoincrement=False)
    payload = db.Column(db.String)

    def __init__(self, id_torrent, payload):
        self.id_torrent = id_torrent
        self.payload = payload


class TorrentsFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_torrent = db.Column(db.Integer, db.ForeignKey('torrents.id'), primary_key=False, autoincrement=False)
    filename = db.Column(db.String)

    def __init__(self, id_torrent, filename):
        self.id_torrent = id_torrent
        self.filename = filename
