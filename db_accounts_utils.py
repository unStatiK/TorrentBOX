# -*- coding: utf-8 -*-

from hashlib import sha256
from flask import session
from sqlalchemy import not_
from account_status import BANNED_ACCOUNT, ADMIN_ACCOUNT, USER_ACCOUNT
from main import SALT_PASS, db
from models import Accounts
from session_keys import USER_TOKEN, USER_ID_TOKEN


def check_login(login, password):
    if login and password:
        password = sha256(password.encode("utf-8")).hexdigest()
        password = "".join([password, SALT_PASS])
        password = sha256(password).hexdigest()
        account = db.session.query(Accounts.status).filter_by(name=login.encode("utf-8"), password=password).limit(
                1).first()
        if account:
            if account.status != BANNED_ACCOUNT:
                return account.status
        return None


def check_admin_session():
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        account = db.session.query(Accounts.status).filter_by(id=int(session[USER_ID_TOKEN])).limit(1).first()
        if account:
            if account.status == ADMIN_ACCOUNT:
                return True
    return None


def get_id_login(login):
    account = db.session.query(Accounts.id).filter_by(name=login).limit(1).first()
    if account:
        return account.id
    return None


def get_all_users():
    return db.session.query(Accounts).filter(not_(Accounts.id == session[USER_ID_TOKEN])) \
        .order_by(Accounts.name).all()


def get_account(user_id):
    return db.session.query(Accounts).filter_by(id=user_id).limit(1).first()


def update_account(user_id, name, password):
    account = get_account(user_id)
    if account:
        account.name = name
        if password != "":
            password = sha256(password.encode("utf-8")).hexdigest()
            password = "".join([password, SALT_PASS])
            password = sha256(password).hexdigest()
            account.password = str(password)
        db.session.commit()


def add_account(name, password):
    password = sha256(password.encode("utf-8")).hexdigest()
    password = "".join([password, SALT_PASS])
    password = sha256(password).hexdigest()
    user = Accounts(name, str(password), USER_ACCOUNT)
    db.session.add(user)
    db.session.commit()


def delete_account(user_id):
    user = get_account(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
