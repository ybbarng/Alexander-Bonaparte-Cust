import json
from datetime import datetime
from datetime import timedelta

from awair import Awair
from awair.enums import DeviceType

from abcust.settings import AWAIR_EMAIL, AWAIR_PASSWORD, AWAIR_ACCESS_TOKEN, AWAIR_DEVICE_ID
from abcust.celery import app
from abcust.tasks import slack


COLORS = ['#2EB886', '#ABA74D', '#DAA038', '#BF511C', '#A30200']


def get_awair():
    return Awair(email=AWAIR_EMAIL, password=AWAIR_PASSWORD, access_token=AWAIR_ACCESS_TOKEN)


def send_to_slack(color, title=None, message=None, fields=None, timestamp=None, log=False):
    slack.write.delay('Cathy', color, title, message, fields, timestamp, log=log)


def send_to_slack_blocking(color, title=None, message=None, fields=None, timestamp=None, log=False):
    slack.write('Cathy', color, title, message, fields, timestamp, log=log)


def _notify_score(score):
    message = '현재 공기질 종합 점수는 {}점입니다.'.format(score.score)
    fields = [
        {
            'title': '온도',
            'value': '{}단계: {} ℃'.format(score.index.temp, score.sensor.temp),
            'short': True,
        },{
            'title': '습도',
            'value': '{}단계: {} %'.format(score.index.humidity, score.sensor.humidity),
            'short': True,
        },{
            'title': '휘발성유기화합물(VOC)',
            'value': '{}단계: {} ppb'.format(score.index.voc, score.sensor.voc),
            'short': True,
        },{
            'title': '초미세먼지(PM2.5)',
            'value': '{}단계: {} µg/m³'.format(score.index.pm25, score.sensor.pm25),
            'short': True,
        },
    ]
    color_index = get_color_of_total_score(score.score)
    send_to_slack(COLORS[color_index], None, message, fields, score.timestamp.timestamp() + (9 * 3600)) # from utc to +09:00


def get_color_of_total_score(total_score):
    color_index = 0
    if total_score <= 80:
        color_index = 4
    elif total_score <= 90:
        color_index = 2
    return color_index


def get_score():
    return get_awair().get_score(DeviceType.AWAIR_MINT, AWAIR_DEVICE_ID)


@app.task
def notify_score():
    _notify_score(get_score())
    return True


@app.task
def get_timelines():
    start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = start_dt + timedelta(days=1)
    timelines = get_awair().get_timelines(DeviceType.AWAIR_MINT, AWAIR_DEVICE_ID, start_dt, end_dt)
    for timeline in timelines:
        print(timeline.timestamp)
        print(timeline.score)
    return timelines


@app.task
def get_inbox_items(start_dt, end_dt):
    return get_awair().get_inbox_items(start_dt, end_dt, 'ko')


def get_inbox_items_batch():
    FILE = 'cathy_last_notified.timestamp'
    MAXIMUM_INTERVAL = 6  # hours

    end_dt = datetime.utcnow()
    last_notified = LastNotified.load()
    start_dt = max(end_dt - timedelta(hours=MAXIMUM_INTERVAL), last_notified.datetime)

    new_notified_dt = notify_new_inbox_item(
        reversed(get_inbox_items(start_dt, end_dt)),
        last_notified.datetime)

    if new_notified_dt > last_notified.datetime:
        notify_score.delay()
        last_notified.datetime = new_notified_dt
        last_notified.save()

    return True


def get_index(inbox_item):
    try:
        return int(inbox_item.icon_url[-5])
    except ValueError:
        fields = [{
            'title': 'URL',
            'value': inbox_item.icon_url,
            'short': False
        }]
        send_to_slack(COLORS[4],
                      message='알림 메시지의 경고 단계를 추정할 수 없습니다.',
                      fields=fields,
                      log=True)
        return 4


def notify_new_inbox_item(inbox_items, last_notified_dt):
    new_notified_dt = datetime.fromtimestamp(0)
    for inbox_item in inbox_items:
        if inbox_item.timestamp <= last_notified_dt:
            continue
        index = get_index(inbox_item)
        fields = [{
            'title': '경고 단계',
            'value': '{} 단계'.format(index),
            'short': False
        }]
        send_to_slack_blocking(COLORS[index],
                      inbox_item.title,
                      inbox_item.description,
                      timestamp=inbox_item.timestamp.timestamp() + (9 * 3600)) # from utc to +09:00
        new_notified_dt = inbox_item.timestamp
    return new_notified_dt


class LastNotified:
    FILE = 'cathy_last_notified.timestamp'

    def __init__(self, timestamp):
        self.datetime = datetime.fromtimestamp(timestamp)

    @classmethod
    def _load_timestamp(cls):
        try:
            with open(cls.FILE, 'r') as f:
                return float(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    @classmethod
    def load(cls):
        return cls(cls._load_timestamp())

    @classmethod
    def _save_timestamp(cls, timestamp):
        with open(cls.FILE, 'w+') as f:
            f.write(str(timestamp))

    def save(self):
        self._save_timestamp(self.datetime.timestamp())


