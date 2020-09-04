import base64
import string
import random


def encode(key):
    random_letter = random.choice(string.ascii_letters)
    return random_letter + base64.urlsafe_b64encode(str(key))


def decode(encoded):
    return base64.urlsafe_b64decode(encoded[1:])

