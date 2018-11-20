from celery import Celery
from flask import session

from abcust.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


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
    return auth_celery.send_task('auth.is_authenticated', args=(access_token,)).get() is not None
