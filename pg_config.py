# -*- coding: utf-8 -*-

from psycopg2cffi import compat

compat.register()

DB_URI = 'postgresql+psycopg2://user:password@host/db'
