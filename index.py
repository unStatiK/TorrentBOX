# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template, redirect, request, session
from flaskext.sqlalchemy import SQLAlchemy
from wtforms import Form, TextField, PasswordField, validators
from hashlib import sha1
from cherrypy import wsgiserver
from sqlalchemy import not_
from sqlalchemy.orm import relationship
import re, os, time, math

app = Flask(__name__)

UPLOAD_FOLDER = '/path/to/torrents/folder/'
ALLOWED_EXTENSIONS = set(['torrent'])

app.secret_key = '\xfcxb6\xd3\xade\xf2!x'

app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 0
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

cherry = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.CherryPyWSGIServer(('127.0.0.1', 8081), cherry)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://<db_user>:<password>@/<db>'
db = SQLAlchemy(app,False)

tags_links = db.Table('tags_links',db.metadata,
    db.Column('id_tags', db.Integer, db.ForeignKey('tags.id')),
    db.Column('id_torrent', db.Integer, db.ForeignKey('torrents.id'))
)

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(255),unique=True)

    def __init__(self, name):
        self.name = name

class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(255),unique=True)
    psw = db.Column(db.String(255))
    status = db.Column(db.Integer)

    def __init__(self, name, psw, status):
        self.name = name
        self.psw = psw
        self.status = status

class Torrents(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    filename = db.Column(db.String(255))
    id_acc = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    size = db.Column(db.Float)
    tags_ = relationship("Tags",secondary=tags_links)

    def __init__(self, name, description, filename, id_acc, size):
        self.name = name
        self.description = description
        self.filename = filename
        self.id_acc = id_acc
        self.size = size

    def _find_tag(self, id_t):
        q = Tags.query.filter_by(id=id_t)
        t = q.first()
        return t

    def _get_tags(self):
        return [x.id for x in self.tags_]

    def _set_tags(self, value):
        for id_t in value:
            self.tags_.append(self._find_tag(id_t))

    str_tags = property(_get_tags,_set_tags)




def tokenize(text, match=re.compile("([idel])|(\d+):|(-?\d+)").match):
    i = 0
    while i < len(text):
        m = match(text, i)
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            yield "s"
            yield text[i:i+int(s)]
            i = i + int(s)
        else:
            yield s

def decode_item(next, token):
    if token == "i":
        data = int(next())
        if next() != "e":
            raise ValueError
    elif token == "s":
        data = next()
    elif token == "l" or token == "d":
        data = []
        tok = next()
        while tok != "e":
            data.append(decode_item(next, tok))
            tok = next()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data

def decode(text):
    try:
        src = tokenize(text)
        data = decode_item(src.next, src.next())
        for token in src:
            raise SyntaxError("trailing junk")
    except (AttributeError, ValueError, StopIteration):
        raise SyntaxError("syntax error")
    return data

class LoginForm(Form):
    log = TextField('Login', [validators.Length(min=3, max=25)])
    psw = PasswordField('Password', [validators.Length(min=3, max=25)])

def check_login(login,password):
  log = db.session.query(Accounts.status).filter_by(name=login.encode("utf-8"),\
                         psw=sha1(password.encode("utf-8")).hexdigest()).limit(1).first()
  if log:
        if log[0] != 0:
  		return log[0]
        else:
        	return None
  else:
        return None

def check_delete(id_u,id_t):
  tr = db.session.query(Torrents.id_acc).filter_by(id=id_t).limit(1).first()
  if tr:
        if tr[0] == id_u:
  		return tr[0]
        else:
        	return None
  else:
        return None

def check_admin_session():
  if 'user' and 'id_u' in session:	
  	tr = db.session.query(Accounts.status).filter_by(id=int(session['id_u'])).limit(1).first()
        if tr:
        	if tr[0] == 2:
  			return tr[0]
        	else:
        		return None
        else:
        	return None
  else:
        return None


def check_change_tag_torrent(id_u,id_t,id_tg):
  tr = db.session.query(Torrents.id_acc).filter_by(id=id_t).limit(1).first()
  if tr:
        if tr[0] == id_u:
  		return tr[0]
        else:
        	return None
  else:
        return None


def get_id_login(login):
  log = db.session.query(Accounts.id).filter_by(name=login).limit(1).first()
  return log[0]

def get_filename_torrent(id_t):
  log = db.session.query(Torrents.filename).filter_by(id=id_t).limit(1).first()
  return log[0]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/logout/')
def logout():
	session.clear()
     	return redirect("/")

@app.route('/', methods=['GET'])
def index():
      	tgs = db.session.query(Tags).order_by(Tags.name).all()
        num = db.session.query(Torrents.size).all()
        if num:
           len_n = len(num)
           num_pages = len_n / 20
           if(num_pages == 0):
           	num_pages = 1
           else:
                if((20 * num_pages) != len_n and (num_pages > 0)):
                	num_pages = num_pages + 1
           size = 0
           for i in num:
           	size = size + i.size 
        page_ = request.args.get('page', None)
        if page_:
                if re.match('^[1-9]{1,3}$',page_):
                        if int(page_) > num_pages:
         	        	return redirect('/')
                        else:
        			trs = db.session.query(Torrents).order_by(Torrents.id).offset((int(page_)-1)*20).limit(20).all()
                		ath= []
                		for tt in trs:
        				auth = db.session.query(Accounts.name).filter_by(id=tt.id_acc).limit(1).first()
                			ath.append(auth.name)
                else:
       	           return redirect('/')
        else:
                page_ = 1
        	trs = db.session.query(Torrents).order_by(Torrents.id).offset(0).limit(20).all()
                ath= []
                for tt in trs:
        		auth = db.session.query(Accounts.name).filter_by(id=tt.id_acc).limit(1).first()
                	ath.append(auth.name)
        if num and size and num_pages and page_:
                size = round(size*0.001,5)
        	if not session.get('user'):
			return render_template('index.html',trs=trs,tgs=tgs,num=len(num),size=size,pages=num_pages,page=int(page_),ath=ath,auth=None)
                else:
                        if check_admin_session():
				return render_template('index.html',trs=trs,tgs=tgs,num=len(num),size=size,pages=num_pages,page=int(page_),ath=ath,auth=True,admin=True)
                        else:
				return render_template('index.html',trs=trs,tgs=tgs,num=len(num),size=size,pages=num_pages,page=int(page_),ath=ath,auth=True)
        else:
        	if not session.get('user'):
			return render_template('index.html',auth=None)
                else:
                        if check_admin_session():
				return render_template('index.html',auth=True,admin=True)
                        else:
				return render_template('index.html',auth=True)

@app.route('/about/')
def about():
	return render_template('about.html')

@app.route('/login/' , methods=['POST','GET'])
def login():
	if request.method == 'POST':
               form = LoginForm(request.form)
               if form.validate() and check_login(form.log.data,form.psw.data):
                session['user'] = form.log.data
                session['id_u'] = get_id_login(form.log.data)
		return redirect('/user_page/')
               else:
                session.pop('user',None)
                session.pop('id_u',None)
		return redirect('/login/?error=login')
        else: 
                error = request.args.get('error', None)
                if error and error == 'login':
        		return render_template('login.html',error=error)
                else:
        		return render_template('login.html',error=None)

@app.route('/tag/<int:id_tag>/')
def tag(id_tag):
        torrents = db.session.query(Torrents).filter(Torrents.id.in_(db.session.query(tags_links.c.id_torrent).\
                                                                filter(tags_links.c.id_tags==id_tag))).all()

	return render_template('tag.html',torrents=torrents)


@app.route('/admin/')
def admin():
        if 'user' and 'id_u' in session :
                if check_admin_session():
                	torrent = db.session.query(Torrents.id,Torrents.filename,Torrents.name).order_by(Torrents.id.desc()).all()
                	tags = db.session.query(Tags).order_by(Tags.name).all()
                	users = db.session.query(Accounts).filter(not_(Accounts.id==session['id_u'])).order_by(Accounts.name).all()
       			return render_template('admin.html',torrent=torrent,tags=tags,users=users)
                else:
                	return "No!!!!"
        else:
        	return "NO!!!!"


@app.route('/admin/tag/edit/<int:id_tag>/', methods=['POST','GET'])
def tag_edit(id_tag):
        if 'user' and 'id_u' in session :
                if request.method == 'POST':
                	if 'tag' in request.form :
                        	if check_admin_session():
					tag = request.form['tag']
                        		tag = tag.strip()
                        		if tag == "":
                                		return redirect('/admin/')

                                	tag_ = db.session.query(Tags).get(id_tag)
                        		tag_.name = tag 
                        		db.session.commit()
                               		return redirect('/admin/')

                else:
                	if check_admin_session():
                		tag = db.session.query(Tags).filter_by(id=id_tag).limit(1).first()
       				return render_template('tag_edit.html',tag=tag)
                	else:
                		return "No!!!!"
        else:
        	return "NO!!!!"



@app.route('/admin/tag/delete/<int:id_tag>/', methods=['POST','GET'])
def tag_delete(id_tag):
        if 'user' and 'id_u' in session :
            if request.method == 'POST':
                if check_admin_session():
            		if 'f_acp' in request.form and request.form['f_acp'] == "yes":
				tag = db.session.query(Tags).get(id_tag)
                       		db.session.delete(tag)
				db.session.commit()
            			return redirect("/admin/")
                	if 'f_no' in request.form and request.form['f_no'] == "no":
          			return redirect("/admin/")
        	else:
        		return redirect('/')

            else:
        	return render_template('tag_delete.html',id_tag=id_tag)
        else:
        	return redirect('/')

@app.route('/admin/user/edit/<int:id_user>/', methods=['POST','GET'])
def user_edit(id_user):
        if 'user' and 'id_u' in session :
                if request.method == 'POST':
                	if 'user' and 'psw' and 'psw_r' in request.form :
                        	if check_admin_session():
					name = request.form['user']
                        		name = name.strip()
					psw = request.form['psw']
                        		psw = psw.strip()
					psw_r = request.form['psw_r']
                        		psw_r = psw_r.strip()
                        		if name == "":
                                		return redirect('/admin/')
                                        if psw == "" and psw_r == "":
                                		user = db.session.query(Accounts).get(id_user)
                        			user.name = name 
                        			db.session.commit()
					elif psw != "" and psw_r != "":
                                        	if psw == psw_r:
                                          		user = db.session.query(Accounts).get(id_user)
                                                        user.name = name
                                                        user.psw = str(sha1(psw).hexdigest())
                                                        db.session.commit()
                               		return redirect('/admin/')

                else:
                	if check_admin_session():
                		user = db.session.query(Accounts).filter_by(id=id_user).limit(1).first()
       				return render_template('user_edit.html',user=user)
                	else:
                		return "No!!!!"
        else:
        	return "NO!!!!"


@app.route('/admin/user/add/', methods=['POST','GET'])
def user_add():
        if 'user' and 'id_u' in session :
                if request.method == 'POST':
                	if 'user' and 'psw' and 'psw_r' in request.form :
                        	if check_admin_session():
					name = request.form['user']
                        		name = name.strip()
					psw = request.form['psw']
                        		psw = psw.strip()
					psw_r = request.form['psw_r']
                        		psw_r = psw_r.strip()
                        		if name != "" and psw != "" and psw_r != "":
                                        	if psw == psw_r:
                                			user = Accounts(name,str(sha1(psw).hexdigest()),1)
                                          		db.session.add(user)
                                                        db.session.commit()
                                			return redirect('/admin/')
                                                else:
                                			return redirect('/admin/')
                               		return redirect('/admin/')

                else:
                	if check_admin_session():
       				return render_template('user_add.html')
                	else:
                		return "No!!!!"
        else:
        	return "NO!!!!"


@app.route('/admin/user/delete/<int:id_user>/', methods=['POST','GET'])
def user_delete(id_user):
        if 'user' and 'id_u' in session :
            if request.method == 'POST':
                if check_admin_session():
            		if 'f_acp' in request.form and request.form['f_acp'] == "yes":
				user = db.session.query(Accounts).get(id_user)
                       		db.session.delete(user)
				db.session.commit()
            			return redirect("/admin/")
                	if 'f_no' in request.form and request.form['f_no'] == "no":
          			return redirect("/admin/")
        	else:
        		return redirect('/')

            else:
        	return render_template('user_delete.html',id_user=id_user)
        else:
        	return redirect('/')



@app.route('/user_page/')
def user():
        if 'user' and 'id_u' in session :
                torrent = db.session.query(Torrents.id,Torrents.filename,Torrents.name).order_by(Torrents.id.desc()).\
                                                                               filter_by(id_acc=session['id_u']).all()
                if torrent:
       			return render_template('user.html',torrent=torrent)
                else:
       			return render_template('user.html')
        else:
        	return redirect('/')


@app.route('/user_page/addtag/', methods=['POST','GET'])
def addtag():
        if 'user' and 'id_u' in session :
            if request.method == 'POST':
                if 'newtag' and 'idt' in request.form :
                        if re.match('^[0-9]{1,3}$',request.form['idt']):
                        	newtag = request.form['newtag'].strip()
                                if newtag != "" and len(newtag) <=20:
                        		newtag = newtag.lower()
                        		trs = db.session.query(Tags).filter_by(name=newtag).limit(1).first()
                        		if not trs:
                        			ntag = Tags(newtag)
                                		db.session.add(ntag)
                                		db.session.commit()
                                		trs_ = db.session.query(Torrents).filter_by(id=int(request.form['idt'])).first()
                                		trs_.str_tags = [ntag.id]
                                		db.session.commit()
                                        	return redirect('/user_page/edit/' + str(request.form['idt']))
        else:
        	return redirect('/')
        return redirect('/user_page/')


@app.route('/user_page/torrent/<int:id_t>/addtag/', methods=['POST','GET'])
def addtag_torrent(id_t):
        if 'user' and 'id_u' in session :
            if request.method == 'POST':
                if 'tag' in request.form :
                        trs = db.session.query(Torrents).filter_by(id=id_t).first()
			trs.str_tags = [request.form['tag']]
			db.session.commit()
            		return redirect("/user_page/edit/" + str(id_t))  
        else:
        	return redirect('/')


@app.route('/user_page/torrent/<int:id_t>/tag/<int:id_tg>/delete/')
def del_tag(id_t,id_tg):
 if 'user' and 'id_u' in session :
 	if not check_admin_session():
        	if not check_change_tag_torrent(session['id_u'],id_t,id_tg):
                	return redirect("/user_page/")
        trs = db.session.query(Torrents).filter_by(id=id_t).first()
        tgs = db.session.query(Tags).filter_by(id=id_tg).first()
        trs.tags_.remove(tgs)
        db.session.commit()
        return redirect("/user_page/edit/" + str(id_t))
 else:
 	return redirect('/')


@app.route('/user_page/edit/<int:id_t>/', methods=['POST','GET'])
def edit(id_t):
        if 'user' and 'id_u' in session :
            if request.method == 'POST':
                if 'f_name' in request.form and 'f_desc' in request.form:
                        f_name = request.form['f_name']
                        f_name = f_name.strip()
                        if f_name == "":
                        	f_name = "null" 
                        f_desc = request.form['f_desc']
                        f_desc = f_desc.strip()
                        if f_desc == "":
                        	f_desc = "null"
			trs = db.session.query(Torrents).get(id_t)
			trs.name = f_name
                        trs.description = f_desc
			db.session.commit()
            		return redirect("/user_page/")  
            else:
                torrent = db.session.query(Torrents.name,Torrents.description).filter_by(id=id_t).limit(1).first()
                all_tags = db.session.query(Tags.id,Tags.name).all()
                tgs = db.session.query(Tags.name,Tags.id).filter(Tags.id.in_(db.session.query(tags_links.c.id_tags).\
                                                            filter(tags_links.c.id_torrent==id_t))).all()
                if torrent:
       			return render_template('edit.html',torrent=torrent,id_t=id_t,tags=tgs,all_tags=all_tags)
                else:
       			return render_template('user.html')
        else:
        	return redirect('/')

@app.route('/user_page/delete/<int:id_t>/', methods=['POST','GET'])
def delete(id_t):
        if 'user' and 'id_u' in session :
            if request.method == 'POST':
            	if 'f_acp' in request.form and request.form['f_acp'] == "yes":
                        if check_delete(session['id_u'],id_t):
                        	filename = get_filename_torrent(id_t)
                               	os.remove(app.config['UPLOAD_FOLDER'] + filename)
				trs = db.session.query(Torrents).get(id_t)
                       		db.session.delete(trs)
				db.session.commit()
            		return redirect("/user_page/")
                if 'f_no' in request.form and request.form['f_no'] == "no":
          		return redirect("/user_page/")
            else:
        	return render_template('delete.html',id_t=id_t)
        else:
        	return redirect('/')

@app.route('/user_page/upload/', methods = ['POST','GET'])
def upload():
	if request.method == 'POST':
                if 'user' and 'id_u' not in session:  
                	if 'name' and 'desc' not in request.form:
        			return redirect('/')
        	file = request.files['file']
        	if file and allowed_file(file.filename):
                        m = time.time()
                        uniqid = '%4x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
            		filename = uniqid + ".torrent"

                        while os.path.exists(app.config['UPLOAD_FOLDER'] + filename) != False:
                        	m = time.time()
                        	uniqid = '%4x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
            			filename = uniqid + ".torrent"
            		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                        try:
                        	data = open(app.config['UPLOAD_FOLDER'] + filename, "rb").read()
                        except IOError:
                        	return redirect('/')
                        if data:
                        	torrent_ = decode(data)
                                size = 0
                                try:
                                	info = torrent_["info"]["files"]
                                	for file in torrent_["info"]["files"]:
                                		size = size + file["length"]
                                	size = round((size*0.001)*0.001,3)
                                except KeyError:
                                	size = torrent_["info"]["length"]    
                                	size = round((size*0.001)*0.001,3)

                        me = Torrents(request.form['name'], request.form['desc'],filename,session['id_u'],size)
                        db.session.add(me)
                        db.session.commit()
            		return redirect('/user_page/')
        return render_template('upload.html')

@app.route('/info/<int:id_t>/')
def info(id_t):
        torrent = db.session.query(Torrents.name,Torrents.filename).filter_by(id=id_t).limit(1).first()
        if torrent:
                try:
			data = open(app.config['UPLOAD_FOLDER'] + torrent.filename, "rb").read()
                except IOError:
                	return redirect('/')
                if data:
			torrent_ = decode(data)
                        try:
				return render_template('info.html',torrent=torrent,info=torrent_["info"]["files"])
                        except KeyError:
				return render_template('info.html',torrent=torrent,info=torrent_,f_er=1)
                else:
			return render_template('info.html',torrent=torrent,info=None)
        else:
		return redirect('/')


@app.errorhandler(404)
def not_found(error):
	return redirect('/')

#@app.errorhandler(500)
#def server_error(error):
#	return redirect('/')

if __name__ == '__main__':
	try:
		server.start()
	except KeyboardInterrupt:
		server.stop()





