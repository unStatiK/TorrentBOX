# -*- coding: utf-8 -*-

from hashlib import sha256
from hurry.filesize import size
import time
import math
import enum

from main import PASSWORD_SALT


def generate_password_hash(password):
    password = sha256(password.encode("utf-8")).hexdigest()
    password = "".join([password, PASSWORD_SALT])
    return sha256(password.encode('utf-8')).hexdigest()


def uniqid():
    local_time = time.time()
    return '%4x%05x' % (math.floor(local_time), math.floor((local_time - math.floor(local_time)) * 1000000))


class SizeUnit(enum.Enum):
    BYTES = 'bytes'
    KB = 'Kb'
    MB = 'Mb'
    GB = 'Gb'
    TB = 'Tb'


marked_units = [
    (1024 ** 4, " #%s" % SizeUnit.TB.value),
    (1024 ** 3, " #%s" % SizeUnit.GB.value),
    (1024 ** 2, " #%s" % SizeUnit.MB.value),
    (1024 ** 1, " #%s" % SizeUnit.KB.value),
    (1024 ** 0, " #%s" % SizeUnit.BYTES.value)
]


def convert_unit(size_in_bytes):
    human_size = size(size_in_bytes, system=marked_units)
    unit = human_size[human_size.index('#') + 1:len(human_size)]
    rounded_size = size_in_bytes
    if unit == SizeUnit.KB.value:
        rounded_size = round(size_in_bytes / 1024, 1)
    if unit == SizeUnit.MB.value:
        rounded_size = round(size_in_bytes / (1024 * 1024), 1)
    if unit == SizeUnit.GB.value:
        rounded_size = round(size_in_bytes / (1024 * 1024 * 1024), 1)
    if unit == SizeUnit.TB.value:
        rounded_size = round(size_in_bytes / (1024 * 1024 * 1024 * 1024), 1)
    return "%s %s" % (rounded_size, unit)
