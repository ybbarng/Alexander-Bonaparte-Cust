import base64
import zlib

import bson
from celery import Celery
from flask import session
from rfc7539 import aead

from abcust.settings import AUTH_AEAD_SECRET, CELERY_BROKER_URL, CELERY_RESULT_BACKEND


auth_celery = Celery('auth',
                     broker=CELERY_BROKER_URL,
                     backend=CELERY_RESULT_BACKEND)
auth_celery.conf.task_default_queue = 'auth'


def access_token_issued(request):
    access_token = request.args.get('access_token')
    if access_token:
        session['access_token'] = access_token
        session.permanent = True  # default 31 days
    return access_token is not None


def authorized(request):
    access_token = session.get('access_token')
    if access_token:
        return verify(access_token)
    else:
        return False


def verify(access_token):
    try:
        token = decrypt_token(AUTH_AEAD_SECRET, access_token)
        if token['app'] == 'remote controller':
            return auth_celery.send_task(
                'auth.is_authenticated',
                args=(token['app'], token['user_id'], token['user_name'])
            ).get()
    except:
        return False


def decrypt_token(key, token):
    token = base64.urlsafe_b64decode(token)
    token = zlib.decompress(token)
    token = bson.loads(token)
    result = aead.verify_and_decrypt(key, token['nonce'], token['ciphertext'], token['tag'], token['header'])
    return bson.loads(result)
