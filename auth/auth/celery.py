from celery import Celery

from auth.models import *
from auth.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from auth.utils import my_hash


auth_celery = Celery('auth',
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND)

auth_celery.conf.timezone = 'Asia/Seoul'
auth_celery.conf.task_default_queue = 'auth'


@auth_celery.task(name='auth.is_authenticated')
def is_authenticated(app_name, user_id, user_name):
    try:
        user = User.get(name=user_name)
        app = App.get(name=app_name)
        return my_hash(app.hash_secret, user.id)
    except:
        return False


if __name__ == '__main__':
    auth_celery.start()
