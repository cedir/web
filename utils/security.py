import base64


def encode(key):
    return base64.urlsafe_b64encode(str(key))


def decode(encoded):
    return base64.urlsafe_b64decode(encoded)

