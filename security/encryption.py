import base64
import string
import random


def encode(key):
    random_letter =  bytes(random.choice(string.ascii_letters), 'ascii')
    return random_letter + base64.urlsafe_b64encode(bytes(str(key), 'ascii'))


def decode(encoded):
    return base64.urlsafe_b64decode(encoded[1:])

