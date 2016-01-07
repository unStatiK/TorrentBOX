# -*- coding: utf-8 -*-

from models import *
from main import PAGE_TORRENT_COUNT
from sqlalchemy import not_


def fetch_tags():
    return db.session.query(Tags).order_by(Tags.name).all()


def fetch_tag_by_name(name):
    return db.session.query(Tags).filter_by(name=name).limit(1).first()


def fetch_torrents_size():
    info = {}
    torrents = db.session.query(Torrents.size).all()
    size = 0
    for item in torrents:
        size = size + item.size
    info['size'] = size
    info['count'] = len(torrents)
    return info


def get_torrents_pages_count():
    torrents = db.session.query(Torrents.size).all()
    pages_count = 0
    if torrents:
        torrents_count = len(torrents)
        pages_count = torrents_count / PAGE_TORRENT_COUNT
        if pages_count == 0:
            pages_count = 1
        else:
            if (20 * pages_count) != torrents_count and (pages_count > 0):
                pages_count += 1
    return pages_count


def fetch_torrents_page(page):
    torrents_page = {}
    torrents_page['items'] = []
    torrents_page['owners'] = []

    try:
        page = int(page)
        if page > 0:
            torrents_collection = db.session.query(Torrents).order_by(Torrents.id).offset(
                (page - 1) * PAGE_TORRENT_COUNT).limit(PAGE_TORRENT_COUNT).all()
            torrents_owners = {}
            for item in torrents_collection:
                account = db.session.query(Accounts.name).filter_by(id=item.id_acc).limit(1).first()
                torrents_owners[item.id] = account.name
            torrents_page['items'] = torrents_collection
            torrents_page['owners'] = torrents_owners
        return torrents_page
    except Exception:
        return torrents_page


def check_allow_change_torrent_tag(user_id, torrent_id):
    torrent = db.session.query(Torrents.id_acc).filter_by(id=torrent_id).limit(1).first()
    if torrent:
        if torrent.id_acc == user_id:
            return True
    return False


def check_allow_torrent_delete(user_id, torrent_id):
    torrent = db.session.query(Torrents.id_acc).filter_by(id=torrent_id).limit(1).first()
    if torrent:
        if torrent.id_acc == user_id:
            return True
    return False


def get_torrent_filename(torrent_id):
    torrent = db.session.query(Torrents.filename).filter_by(id=torrent_id).limit(1).first()
    if torrent:
        return torrent.filename


def fetch_torrents_by_tag(tag_id):
    return db.session.query(Torrents).filter(Torrents.id.in_(db.session.query(tags_links.c.id_torrent).
                                                             filter(tags_links.c.id_tags == tag_id))).all()


def fetch_tags_by_torrent(torrent_id):
    return db.session.query(Tags).filter(Tags.id.in_(db.session.query(tags_links.c.id_tags).
                                                     filter(tags_links.c.id_torrent == torrent_id))).all()


def search_torrents(pattern):
    founded_torrents = []
    search_pattern = "".join(['%', pattern, '%'])
    torrents = db.session.query(Torrents).filter(Torrents.name.like(search_pattern)).all()

    torrent_id_collection = []
    for item in torrents:
        founded_torrents.append(item)
        torrent_id_collection.append(item.id)
    if len(torrent_id_collection) > 0:
        torrents_by_desc = db.session.query(Torrents).filter(not_(Torrents.id.in_(torrent_id_collection)),
                                                             Torrents.description.like(search_pattern)).all()
        founded_torrents = founded_torrents + torrents_by_desc
    else:
        torrents_by_desc = db.session.query(Torrents).filter(Torrents.description.like(search_pattern)).all()
        founded_torrents = founded_torrents + torrents_by_desc
    return founded_torrents


def get_all_torrents():
    return db.session.query(Torrents).order_by(Torrents.id.desc()).all()


def get_all_tags():
    return db.session.query(Tags).order_by(Tags.name).all()


def update_tag_name(tag_id, name):
    tag_ = db.session.query(Tags).get(tag_id)
    tag_.name = name
    db.session.commit()


def get_tag_by_id(tag_id):
    return db.session.query(Tags).filter_by(id=tag_id).limit(1).first()


def delete_tag(tag_id):
    tag = get_tag_by_id(tag_id)
    if tag:
        db.session.delete(tag)
        db.session.commit()


def add_tag(torrent_id, name):
    tag = Tags(name)
    db.session.add(tag)
    db.session.commit()

    torrents_ = db.session.query(Torrents).filter_by(id=torrent_id).first()
    torrents_.str_tags = [tag.id]
    db.session.commit()


def fetch_torrents_by_account(user_id):
    return db.session.query(Torrents).order_by(Torrents.id.desc()).filter_by(id_acc=user_id).all()


def get_torrent_by_id(torrent_id):
    return db.session.query(Torrents).filter_by(id=torrent_id).first()


def attache_tag(torrent_id, user_id, tag_name):
    torrent = get_torrent_by_id(torrent_id)
    if torrent.id_acc == user_id:
        torrent.str_tags = [tag_name]
        db.session.commit()


def delete_torrents_tag(torrent_id, tag_id):
    torrent = db.session.query(Torrents).filter_by(id=torrent_id).first()
    tag = db.session.query(Tags).filter_by(id=tag_id).first()
    if torrent and tag:
        torrent.tags_.remove(tag)
        db.session.commit()


def update_torrent(torrent_id, user_id, filename, description):
    torrent = get_torrent_by_id(torrent_id)
    if torrent and torrent.id_acc == user_id and filename != "":
        torrent.name = filename
        torrent.description = description
        db.session.commit()


def delete_torrent(torrent_id):
    torrent = db.session.query(Torrents).get(torrent_id)
    if torrent:
        db.session.delete(torrent)
        db.session.commit()


def add_torrent(name, desc, filename, user_id, size):
    me = Torrents(name, desc, filename, user_id, size)
    db.session.add(me)
    db.session.commit()
