# -*- coding: utf-8 -*-

from models import *
from main import PAGE_TORRENT_COUNT, TORRENTS_STAT_ROW_ID
from sqlalchemy import not_, func


def fetch_tags():
    return db.session.query(Tags).order_by(Tags.name).all()


def fetch_tag_by_name(name):
    return db.session.query(Tags).filter_by(name=name).limit(1).first()


def fetch_torrents_size():
    info = {}
    torrents_count = db.session.query(func.count(Torrents.id)).scalar()
    torrents_size = db.session.query(TorrentsStat.size).filter_by(id=TORRENTS_STAT_ROW_ID).limit(1).first()
    size = 0
    if torrents_size:
       size =  torrents_size.size
    info['size'] = size
    info['count'] = torrents_count
    return info


def get_torrents_pages_count():
    torrents_count = db.session.query(func.count(Torrents.id)).scalar()
    pages_count = 0
    if torrents_count:
        pages_count = int(torrents_count / PAGE_TORRENT_COUNT)
        if pages_count == 0:
            pages_count = 1
        else:
            if (PAGE_TORRENT_COUNT * pages_count) != torrents_count and (pages_count > 0):
                pages_count += 1
    return pages_count


def fetch_torrents_page(page):
    torrents_page = {'items': [], 'owners': []}
    try:
        page = int(page)
        if page > 0:
            torrents_collection = db.session.query(Torrents).order_by(Torrents.id).offset(
                (page - 1) * PAGE_TORRENT_COUNT).limit(PAGE_TORRENT_COUNT).all()
            torrents_owners = {}
            accounts_ids = []
            for item in torrents_collection:
                accounts_ids.append(item.id_acc)
            accounts = db.session.query(Accounts.id, Accounts.name).filter(Accounts.id.in_(accounts_ids)).all()
            for account in accounts:
                torrents_owners[account.id] = account.name
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
    torrents = db.session.query(Torrents).filter(Torrents.name.ilike(search_pattern)).all()
    torrent_id_collection = []
    for item in torrents:
        founded_torrents.append(item)
        torrent_id_collection.append(item.id)
    torrents_by_desc = []
    if len(torrent_id_collection) > 0:
        torrents_by_desc = db.session.query(Torrents).filter(not_(Torrents.id.in_(torrent_id_collection)),
                                                             Torrents.description.ilike(search_pattern)).all()
        founded_torrents = founded_torrents + torrents_by_desc
    else:
        torrents_by_desc = db.session.query(Torrents).filter(Torrents.description.ilike(search_pattern)).all()
        founded_torrents = founded_torrents + torrents_by_desc
    for item in torrents_by_desc:
        torrent_id_collection.append(item.id)

    if len(torrent_id_collection) > 0:
        torrents_by_filename = db.session.query(TorrentsFiles).filter(not_(TorrentsFiles.id_torrent.in_(torrent_id_collection)),
                                                             TorrentsFiles.filename.ilike(search_pattern)).all()
        if torrents_by_filename:
            current_torrents_ids = []
            for torrent in torrents_by_filename:
                current_torrents_ids.append(torrent.id)
            torrents = db.session.query(Torrents).filter(Torrents.id.in_(current_torrents_ids)).all()
            founded_torrents = founded_torrents + torrents
    else:
        torrents_by_filename = db.session.query(TorrentsFiles).filter(TorrentsFiles.filename.ilike(search_pattern)).all()
        if torrents_by_filename:
            current_torrents_ids = []
            for torrent in torrents_by_filename:
                current_torrents_ids.append(torrent.id)
            torrents = db.session.query(Torrents).filter(Torrents.id.in_(current_torrents_ids)).all()
            founded_torrents = founded_torrents + torrents

    return founded_torrents


def get_all_torrents():
    return db.session.query(Torrents).order_by(Torrents.id.desc()).all()


def get_all_tags():
    return db.session.query(Tags).order_by(Tags.name).all()


def update_tag_name(tag_id, name):
    try:
        tag_ = db.session.query(Tags).get(tag_id)
        tag_.name = name
        db.session.commit()
    except:
        db.session.rollback()
        raise


def get_tag_by_id(tag_id):
    return db.session.query(Tags).filter_by(id=tag_id).limit(1).first()


def delete_tag(tag_id):
    tag = get_tag_by_id(tag_id)
    if tag:
        try:
            db.session.delete(tag)
            db.session.commit()
        except:
            db.session.rollback()
            raise


def add_tag(torrent_id, name):
    try:
        tag = Tags(name)
        db.session.add(tag)
        db.session.commit()
        torrents_ = db.session.query(Torrents).filter_by(id=torrent_id).first()
        torrents_.str_tags = [tag.id]
        db.session.commit()
    except:
        db.session.rollback()
        raise


def fetch_torrents_by_account(user_id):
    return db.session.query(Torrents).order_by(Torrents.id.desc()).filter_by(id_acc=user_id).all()


def get_torrent_by_id(torrent_id):
    return db.session.query(Torrents).filter_by(id=torrent_id).first()


def attache_tag(torrent_id, user_id, tag_name):
    torrent = get_torrent_by_id(torrent_id)
    if torrent.id_acc == user_id:
        try:
            torrent.str_tags = [tag_name]
            db.session.commit()
        except:
            db.session.rollback()
            raise


def delete_torrents_tag(torrent_id, tag_id):
    torrent = db.session.query(Torrents).filter_by(id=torrent_id).first()
    tag = db.session.query(Tags).filter_by(id=tag_id).first()
    if torrent and tag:
        try:
            torrent.tags_.remove(tag)
            db.session.commit()
        except:
            db.session.rollback()
            raise


def update_torrent(torrent_id, user_id, filename, description):
    torrent = get_torrent_by_id(torrent_id)
    if torrent and torrent.id_acc == user_id and filename != "":
        try:
            torrent.name = filename
            torrent.description = description
            db.session.commit()
        except:
            db.session.rollback()
            raise


def delete_torrent(torrent_id):
    torrent = db.session.query(Torrents).get(torrent_id)
    if torrent:
        try:
            db.session.delete(torrent)
            db.session.commit()
        except:
            db.session.rollback()
            raise


def add_torrent(name, desc, filename, user_id, size):
    try:
        me = Torrents(name, desc, filename, user_id, size)
        db.session.add(me)
        db.session.commit()
        return me.id
    except:
        db.session.rollback()
        raise

def add_torrent_with_payload(name, desc, filename, user_id, size, payload):
    new_id = None
    try:
        me = Torrents(name, desc, filename, user_id, size)
        db.session.add(me)
        db.session.commit()
        new_id = me.id
        torrent_payload = TorrentsData(new_id, payload)
        db.session.add(torrent_payload)
        db.session.commit()
        return new_id
    except:
        db.session.rollback()
        if new_id:
            delete_torrent(new_id)
        raise

def add_torrent_files_and_size(files, torrent_id, size):
    try:
        for file in files:
            tf = TorrentsFiles(torrent_id, file)
            db.session.add(tf)
            db.session.flush()
        torrents_size = get_torrents_stat_size()
        if torrents_size:
            new_size = torrents_size.size + size
            update_torrents_stat_size(new_size)
        else:
            save_new_torrents_stat_size(size)
        if files:
            db.session.commit()
    except:
        db.session.rollback()
        raise


def get_torrent_payload(torrent_id):
    return db.session.query(TorrentsData.payload).filter_by(id_torrent=torrent_id).limit(1).first()


def get_torrents_stat_size():
    return db.session.query(TorrentsStat.size).filter_by(id=TORRENTS_STAT_ROW_ID).limit(1).first()


def get_torrents_stat_by_id(id):
    return db.session.query(TorrentsStat).filter_by(id=id).first()


def save_new_torrents_stat_size(size):
    try:
        ts = TorrentsStat(TORRENTS_STAT_ROW_ID, size)
        db.session.add(ts)
        db.session.commit()
    except:
        db.session.rollback()
        raise


def update_torrents_stat_size(size):
    torrents_stat = get_torrents_stat_by_id(TORRENTS_STAT_ROW_ID)
    try:
        torrents_stat.size = size
        db.session.commit()
    except:
        db.session.rollback()
        raise
