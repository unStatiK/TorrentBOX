# -*- coding: utf-8 -*-

from hashlib import sha256
import time
import math

from main import SALT_PASS


def generate_password_hash(password):
    password = sha256(password.encode("utf-8")).hexdigest()
    password = "".join([password, SALT_PASS])
    return sha256(password).hexdigest()


def uniqid():
    local_time = time.time()
    return '%4x%05x' % (math.floor(local_time), (local_time - math.floor(local_time)) * 1000000)
