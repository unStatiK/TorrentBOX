# -*- coding: utf-8 -*-

from main import ALLOWED_EXTENSIONS
import re


def tokenize(text, match=re.compile("([idel])|(\d+):|(-?\d+)").match):
    i = 0
    while i < len(text):
        m = match(text, i)
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            yield "s"
            yield text[i:i + int(s)]
            i += int(s)
        else:
            yield s


def decode_item(next_context, token):
    if token == "i":
        data = int(next_context())
        if next_context() != "e":
            raise ValueError
    elif token == "s":
        data = next_context()
    elif token == "l" or token == "d":
        data = []
        tok = next_context()
        while tok != "e":
            data.append(decode_item(next_context, tok))
            tok = next_context()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data


def decode(text):
    #todo check this part
    try:
        src = tokenize(text)
        data = decode_item(src.next, src.next())

        # todo fix condition
        for token in src:
            raise SyntaxError("trailing junk")
    except (AttributeError, ValueError, StopIteration):
        raise SyntaxError("syntax error")
    return data


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
