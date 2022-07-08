# -*- coding: utf-8 -*-

from hashlib import sha256
import time
import math

from main import PASSWORD_SALT


def generate_password_hash(password):
    password = sha256(password.encode("utf-8")).hexdigest()
    password = "".join([password, PASSWORD_SALT])
    return sha256(password.encode('utf-8')).hexdigest()


def uniqid():
    local_time = time.time()
    return '%4x%05x' % (math.floor(local_time), math.floor((local_time - math.floor(local_time)) * 1000000))
