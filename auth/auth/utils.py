from datetime import datetime
import base64
from os import urandom
import zlib

import bson
from csiphash import siphash24
from rfc7539 import aead
from user_agents import parse

from .settings import JWT_KEY, SIPHASH_KEY


def to_user_id(slack_user_id, key=SIPHASH_KEY):
    return my_hash(SIPHASH_KEY, slack_user_id)


def my_hash(key, value):
    return siphash24(key, value.encode('utf-8')).hex()


def get_user_agent(request):
    return str(parse(str(request.user_agent)))


def encrypt(key, message):
    nonce = urandom(12)
    ciphertext, tag = aead.encrypt_and_tag(key, nonce, message, b'')
    #print(aead.verify_and_decrypt(key, nonce, ciphertext, tag, ''))
    return {
        'nonce': nonce,
        'header': b'',
        'ciphertext': ciphertext,
        'tag': tag
    }


def build_token(app, token):
    print('Original: ' + str(token))
    if app:
        token = encrypt(app.aead_secret, bson.dumps(token))
        for k in token:
            token[k] = token[k]
    token = bson.dumps(token)
    token = zlib.compress(token)
    return base64.urlsafe_b64encode(token)


def decrypt_token(app, token):
    token = base64.urlsafe_b64decode(token)
    token = zlib.decompress(token)
    token = bson.loads(token)
    result = aead.verify_and_decrypt(app.aead_secret, token['nonce'], token['ciphertext'], token['tag'], token['header'])
    return bson.loads(result)
