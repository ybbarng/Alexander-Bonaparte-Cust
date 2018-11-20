from celery import Celery
from celery.schedules import crontab

from abcust.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


app = Celery('abcust',
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND,
             include=('abcust.tasks.facebook', 'abcust.tasks.cron'))

app.conf.timezone = 'Asia/Seoul'

app.conf.beat_schedule = {
    'check-awair-notification-every-5-mins': {
        'task': 'abcust.tasks.cron.get_awair_inbox_items',
        'schedule': crontab(minute='*/5'),
    },
    'check-cold-enough-to-turn-off-aircon-during-sleep': {
        'task': 'abcust.tasks.cron.turn_off_aircon_when_cold',
        'schedule': crontab(minute='0', hour='3-9'),
    },
}


if __name__ == '__main__':
    app.start()
