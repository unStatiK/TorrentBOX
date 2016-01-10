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

Python2 compatibility only

Tested work on PyPy 1.8, 1.9, 2.0 beta 1


# Installation

* Install all dependencies

 pip install -r requirements.txt

* Edit config section in main.py

 strongly recommend changed default salt for password

* Create database and run sql script

 psql -u db_user -h db_host db_name < sql/create_pg.sql

* Generate admin account

 python generate_account.py -n account_name -p password > /tmp/create_admin.sql

* Insert admin account into db

 psql -u db_user -h db_host db_name < /tmp/create_admin.sql

* Run it!

 python run.py



