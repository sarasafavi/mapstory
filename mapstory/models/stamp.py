import hashlib


def _stamp(data):
    s = hashlib.sha1()
    s.update(data)
    return s.hexdigest()[0:8]