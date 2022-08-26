# TorrentBOX
This is a web-based torrent archive where you can upload torrent files.  It allows to view, search through and download any file (including ones uploaded by other users) at any time.

#
Used technology:

* Flask micro framework
* SQLAlchemy
* Tornado http server
* WTForms
* Bootstrap grid v2
* PostgreSQL/MySQL/MariaDB

Full UTF-8 support.

Python3 compatibility only.

Compatibility with PyPy3.

# Screenshots

main screen:
![tb1](https://user-images.githubusercontent.com/343531/186961357-a6ec5c9d-0f2a-4c22-b2f1-b1624be7f45e.png)

torrent info page:
![tb2](https://user-images.githubusercontent.com/343531/186961409-b5744d32-8cfb-47ec-8588-f11b97770338.png)
![tb3](https://user-images.githubusercontent.com/343531/186961425-db579c37-602f-4045-bcba-1bc97e423768.png)

user page:
![tb4](https://user-images.githubusercontent.com/343531/186961450-802f9eef-ba2a-44bb-a87a-ab4367ef0e0b.png)

# Installation

* System package dependencies:
  - libpq-dev  // for PostgreSQL
  - libmariadbd-dev // for MariaDB
  - libmysqlclient-dev // for MySQL
  - python-dev    

1. **Install all python dependencies:**

```pip install -r deps/requirements.txt```

For PostgreSQL support
```pip install -r deps/pg.txt```


For MySQL/MariaDB support
```pip install -r deps/mysql.txt```

2. **Edit config section in pg_config.py or mysql_config.py and main.py. Strongly recommend changed default salt for password!**

3. **Create database and run sql script:**

 For PostgreSQL ```psql -U db_user -h db_host db_name < sql/create_pg.sql```
 
 For MySQL/MariaDB ```myql -u db_user -h db_host db_name < sql/create_mysql.sql```

4. **Generate admin account**

 ```python generate_account.py -n account_name -p password > /tmp/create_admin.sql```

5. **Insert admin account into db**

 For PostgreSQL ```psql -U db_user -h db_host db_name < /tmp/create_admin.sql```
 
 For MySQL/MariaDB ```myql -u db_user -h db_host db_name < /tmp/create_admin.sql```

6. **Run it!**

 ```python run.py```
 
 open http://localhost:8080/ for profit!
 
 start with http://localhost:8080/login login page!


# Installation for PyPy

1. **Install pip module**

```./pypy-xxx/bin/pypy -m ensurepip```

2. **Upgrade pip to latest version**

```./pypy-xxx/bin/pypy -mpip install -U pip wheel```

3. **Install all python dependencies:**

```./pypy-xxx/bin/pypy -mpip install  -r deps/requirements.txt```

For PostgreSQL ```./pypy-xxx/bin/pypy -mpip install  -r deps/pg.txt```

For MySQL/MariaDB ```./pypy-xxx/bin/pypy -mpip install  -r deps/mysql.txt```

4. **Repeat 2-5 steps installation instruction**

5. **Run it!**

```./pypy-xxx/bin/pypy run.py```

# Deploy

Example command for start service:

```nohup python run.py > /dev/null 2>&1```
