# -*- coding: utf-8 -*-

import time

import math


def uniqid():
    local_time = time.time()
    return '%4x%05x' % (math.floor(local_time), (local_time - math.floor(local_time)) * 1000000)
