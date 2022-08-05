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

class SIZE_UNIT(enum.Enum):
   BYTES = 'bytes'
   KB = 'Kb'
   MB = 'Mb'
   GB = 'Gb'
   TB = 'Tb'

marked_units = [
    (1024 ** 4, " #%s" % SIZE_UNIT.TB.value),
    (1024 ** 3, " #%s" % SIZE_UNIT.GB.value),
    (1024 ** 2, " #%s" % SIZE_UNIT.MB.value),
    (1024 ** 1, " #%s" % SIZE_UNIT.KB.value),
    (1024 ** 0, " #%s" % SIZE_UNIT.BYTES.value)
]
def convert_unit(size_in_bytes):
    human_size = size(size_in_bytes, system=marked_units)
    unit = human_size[human_size.index('#') + 1:len(human_size)]
    rounded_size = size_in_bytes
    if unit == SIZE_UNIT.KB.value:
        rounded_size = round(size_in_bytes / 1024, 1)
    if unit == SIZE_UNIT.MB.value:
        rounded_size = round(size_in_bytes / (1024 * 1024), 1)
    if unit == SIZE_UNIT.GB.value:
        rounded_size = round(size_in_bytes / (1024 * 1024 * 1024), 1)
    if unit == SIZE_UNIT.TB.value:
        rounded_size = round(size_in_bytes / (1024 * 1024 * 1024 * 1024), 1)
    return "%s %s" % (rounded_size, unit)

