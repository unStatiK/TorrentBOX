# TorrentBOX

# web torrent archive engine

Used technology:

* Flask micro framework
* SQLAlchemy
* Tornado http server
* WTForms
* Bootstrap grid v2
* PostgreSQL
etc...

Full UTF-8 support

Python3 compatibility only

Compatibility with PyPy3


# Installation

* System package dependencies
  - libpq-dev
  - python-dev    

* Install all python dependencies

 pip install -r requirements.txt

* Edit config section in main.py

 strongly recommend changed default salt for password

* Create database and run sql script

 psql -U db_user -h db_host db_name < sql/create_pg.sql

* Generate admin account

 python generate_account.py -n account_name -p password > /tmp/create_admin.sql

* Insert admin account into db

 psql -U db_user -h db_host db_name < /tmp/create_admin.sql

* Run it!

 python run.py
 
 open http://localhost:8080/ for profit!
 
 
* http://localhost:8080/login  - login page


