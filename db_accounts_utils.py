# -*- coding: utf-8 -*-


from flask import session
from sqlalchemy import not_
from account_status import BANNED_ACCOUNT, ADMIN_ACCOUNT, USER_ACCOUNT
from main import db
from models import Accounts
from session_keys import USER_TOKEN, USER_ID_TOKEN
from utils import generate_password_hash


def check_login(login, password):
    if login and password:
        password = generate_password_hash(password)
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
    return db.session.query(Accounts).filter(not_(Accounts.id == int(session[USER_ID_TOKEN]))) \
        .order_by(Accounts.name).all()


def get_account(user_id):
    return db.session.query(Accounts).filter_by(id=user_id).limit(1).first()


def update_account(user_id, name, password):
    account = get_account(user_id)
    if account:
        try:
            account.name = name
            if password != "":
                password = generate_password_hash(password)
                account.password = str(password)
            db.session.commit()
        except:
            db.session.rollback()
            raise


def add_account(name, password):
    password = generate_password_hash(password)
    try:
        user = Accounts(name, str(password), USER_ACCOUNT)
        db.session.add(user)
        db.session.commit()
    except:
        db.session.rollback()
        raise


def delete_account(user_id):
    user = get_account(user_id)
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            db.session.rollback()
            raise
