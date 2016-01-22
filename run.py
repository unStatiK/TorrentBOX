# -*- coding: utf-8 -*-

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask import render_template, redirect, request, abort
from werkzeug.utils import secure_filename

from db_accounts_utils import *
from db_torrents_utils import *
from helpers import torrent_full_delete, upload_torrent_file
from main import app, APP_HOST, APP_PORT
from session import LoginForm
from session_keys import USER_TOKEN, USER_ID_TOKEN
from torrent_utils import allowed_file, decode
from utils import uniqid

import os
import re


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = uniqid()
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token


@app.route('/logout/')
def logout():
    session.clear()
    return redirect("/")


@app.route('/', methods=['GET'])
def index():
    page_ = request.args.get('page', None)
    page_count = get_torrents_pages_count()
    if page_:
        if re.match("^[1-9]{{1,{0}}}$".format(2 ** 31), page_):
            page_ = int(page_)
            if page_ < 1 or page_ > page_count:
                return redirect('/')
    else:
        page_ = 1

    is_auth = None
    if session.get(USER_TOKEN):
        is_auth = True

    is_admin = check_admin_session()

    torrents_size_info = fetch_torrents_size()
    torrents_size = torrents_size_info['size']

    if torrents_size > 0 and page_count > 0 and page_:
        torrents_size = round(torrents_size * 0.001, 5)
        tags = fetch_tags()

        torrents_page = fetch_torrents_page(page_)
        return render_template('index.html', torrents=torrents_page['items'], tags=tags,
                               count=torrents_size_info['count'], size=torrents_size,
                               pages=page_count,
                               page=page_, authors=torrents_page['owners'], auth=is_auth, admin=is_admin)

    return render_template('index.html', auth=is_auth, admin=is_admin)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate() and check_login(form.login.data, form.password.data):
            session[USER_TOKEN] = form.login.data
            session[USER_ID_TOKEN] = int(get_id_login(form.login.data))
            return redirect('/user_page/')
        else:
            session.pop(USER_TOKEN, None)
            session.pop(USER_ID_TOKEN, None)
            return redirect('/login/?error=login')
    else:
        error = request.args.get('error', None)
        if error and error == 'login':
            return render_template('login.html', error=error)
        else:
            return render_template('login.html', error=None)


@app.route('/tag/<int:id_tag>/')
def tag(id_tag):
    torrents = fetch_torrents_by_tag(id_tag)
    return render_template('tag.html', torrents=torrents)


@app.route('/search/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        if 'pattern' in request.form:
            pattern = request.form['pattern'].strip()
            if pattern != "":
                torrents = search_torrents(pattern)
                return render_template('search.html', torrents=torrents)
    return redirect('/')


@app.route('/admin/')
def admin():
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if check_admin_session():
            torrents = get_all_torrents()
            tags = get_all_tags()
            users = get_all_users()
            return render_template('admin.html', torrents=torrents, tags=tags, users=users)


@app.route('/admin/tag/edit/<int:id_tag>/', methods=['POST', 'GET'])
def tag_edit(id_tag):
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if 'tag' in request.form:
                if check_admin_session():
                    tag = request.form['tag'].strip()
                    if not tag == "":
                        update_tag_name(id_tag, tag)

        else:
            if check_admin_session():
                tag = get_tag_by_id(id_tag)
                return render_template('tag_edit.html', tag=tag)

    return redirect('/admin/')


@app.route('/admin/tag/delete/<int:id_tag>/', methods=['POST', 'GET'])
def tag_delete(id_tag):
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if check_admin_session():
                if 'accept' in request.form and request.form['accept'] == "yes":
                    delete_tag(id_tag)
                return redirect("/admin/")
            else:
                return redirect('/')

        else:
            return render_template('tag_delete.html', id_tag=id_tag)
    return redirect('/')


@app.route('/admin/user/edit/<int:id_user>/', methods=['POST', 'GET'])
def user_edit(id_user):
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if USER_TOKEN in request.form and 'password' in request.form and 're_password' in request.form:
                if check_admin_session():
                    name = request.form[USER_TOKEN].strip()
                    password = request.form['password'].strip()
                    re_password = request.form['re_password'].strip()
                    if name == "":
                        return redirect('/admin/')
                    if password == re_password:
                        update_account(id_user, name, password)
                    return redirect('/admin/')

        else:
            if check_admin_session():
                user_context = get_account(id_user)
                return render_template('user_edit.html', user=user_context)
    return redirect('/')


@app.route('/admin/user/add/', methods=['POST', 'GET'])
def user_add():
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if USER_TOKEN in request.form and 'password' in request.form and 're_password' in request.form:
                if check_admin_session():
                    name = request.form[USER_TOKEN].strip()
                    password = request.form['password'].strip()
                    re_password = request.form['re_password'].strip()
                    if name != "" and password != "" and re_password != "":
                        if password == re_password:
                            add_account(name, password)
                    return redirect('/admin/')
        else:
            if check_admin_session():
                return render_template('user_add.html')


@app.route('/admin/user/delete/<int:id_user>/', methods=['POST', 'GET'])
def user_delete(id_user):
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if check_admin_session():
                if 'accept' in request.form and request.form['accept'] == "yes":
                    delete_account(id_user)
                return redirect("/admin/")
        else:
            return render_template('user_delete.html', id_user=id_user)
    return redirect('/')


@app.route('/user_page/')
def user():
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if isinstance(session[USER_ID_TOKEN], int):
            user_id = session[USER_ID_TOKEN]
            torrents = fetch_torrents_by_account(user_id)
            return render_template('user.html', torrents=torrents)
    else:
        return redirect('/')


@app.route('/user_page/addtag/', methods=['POST', 'GET'])
def addtag():
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if 'newtag' in request.form and 'torrent_id' in request.form:
                if re.match('^[0-9]{1,3}$', request.form['torrent_id']):
                    torrent_id = int(request.form['torrent_id'])
                    newtag = request.form['newtag'].strip()
                    if newtag != "" and len(newtag) <= 20:
                        newtag = newtag.lower()
                        tags = fetch_tag_by_name(newtag)
                        if not tags:
                            add_tag(torrent_id, newtag)
                            return redirect('/user_page/edit/' + str(request.form['torrent_id']))
    else:
        return redirect('/')
    return redirect('/user_page/')


@app.route('/user_page/torrent/<int:id_torrent>/addtag/', methods=['POST', 'GET'])
def addtag_torrent(id_torrent):
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if 'tag' in request.form and isinstance(session[USER_ID_TOKEN], int):
                user_id = int(session[USER_ID_TOKEN])
                tag = str(request.form['tag'])
                attache_tag(id_torrent, user_id, tag)
                return redirect("/user_page/edit/" + str(id_torrent))
    else:
        return redirect('/')


@app.route('/user_page/torrent/<int:torrent_id>/tag/<int:tag_id>/delete/')
def del_tag(torrent_id, tag_id):
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if not check_admin_session():
            if isinstance(session[USER_ID_TOKEN], int):
                user_id = session[USER_ID_TOKEN]
                if not check_allow_change_torrent_tag(user_id, torrent_id):
                    return redirect("/user_page/")
        delete_torrents_tag(torrent_id, tag_id)
        return redirect("/user_page/edit/" + str(torrent_id))
    else:
        return redirect('/')


@app.route('/user_page/edit/<int:torrent_id>/', methods=['POST', 'GET'])
def edit(torrent_id):
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if 'file_name' in request.form and 'file_desc' in request.form:
                file_name = request.form['file_name'].strip()
                file_desc = request.form['file_desc'].strip()
                if isinstance(session[USER_ID_TOKEN], int):
                    user_id = int(session[USER_ID_TOKEN])
                    update_torrent(torrent_id, user_id, file_name, file_desc)
                return redirect("/user_page/")
        else:
            torrent = get_torrent_by_id(torrent_id)
            all_tags = get_all_tags()
            tags = fetch_tags_by_torrent(torrent_id)
            if torrent:
                return render_template('edit.html', torrent=torrent, torrent_id=torrent_id, tags=tags,
                                       all_tags=all_tags)
            else:
                return render_template('user.html')
    else:
        return redirect('/')


@app.route('/user_page/delete/<int:id_torrent>/', methods=['POST', 'GET'])
def delete(id_torrent):
    if USER_TOKEN in session and USER_ID_TOKEN in session:
        if request.method == 'POST':
            if 'accept' in request.form and request.form['accept'] == "yes":
                if isinstance(session[USER_ID_TOKEN], int):
                    user_id = int(session[USER_ID_TOKEN])
                    if check_allow_torrent_delete(user_id, id_torrent):
                        torrent_full_delete(id_torrent)
            return redirect("/user_page/")
        else:
            return render_template('delete.html', id_t=id_torrent)
    return redirect('/')


@app.route('/user_page/upload/', methods=['POST', 'GET'])
def upload():
    if USER_TOKEN not in session and USER_ID_TOKEN not in session:
        return redirect('/')

    if request.method == 'POST':
        if 'name' in request.form and 'desc' in request.form:

            name = request.form['name'].strip()
            description = request.form['desc'].strip()
            file_context = request.files['file']
            filename = secure_filename(file_context.filename)

            if file_context and allowed_file(filename):
                uid = uniqid()
                filename = "".join([uid, ".torrent"])
                upload_torrent_file(name, description, file_context, filename)
                return redirect('/user_page/')
    return render_template('upload.html')


@app.route('/info/<int:id_torrent>/')
def info(id_torrent):
    torrent = get_torrent_by_id(id_torrent)
    if torrent:
        try:
            data = open(app.config['UPLOAD_FOLDER'] + torrent.filename, "rb").read()
        except IOError:
            return redirect('/')

        # todo rewrite try and template
        if data:
            torrent_ = decode(data)
            try:
                return render_template('info.html', torrent=torrent, info=torrent_["info"]["files"])
            except KeyError:
                return render_template('info.html', torrent=torrent, info=torrent_, error=True)
        else:
            return render_template('info.html', torrent=torrent, info=None)
    else:
        return redirect('/')


@app.errorhandler(404)
def not_found(error):
    if not app.config['DEBUG']:
        return redirect('/')


@app.errorhandler(500)
def server_error(error):
    if not app.config['DEBUG']:
        return redirect('/')


if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(APP_PORT, APP_HOST)
    IOLoop.instance().start()
