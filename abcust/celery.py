import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv


load_dotenv()


broker_url = os.getenv('BROKER_URL')
result_backend = os.getenv('CELERY_RESULT_BACKEND')


app = Celery('abcust',
             broker=broker_url,
             backend=result_backend,
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
