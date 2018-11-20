from celery import Celery
from celery.schedules import crontab

from abcust.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


app = Celery('abcust',
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND,
             include=('abcust.tasks.facebook',))

app.conf.timezone = 'Asia/Seoul'

app.conf.beat_schedule = {
    'check-awair-notification-every-5-mins': {
        'task': 'abcust.tasks.cathy.get_inbox_items_batch',
        'schedule': crontab(minute='*/5'),
    },
}


if __name__ == '__main__':
    app.start()
