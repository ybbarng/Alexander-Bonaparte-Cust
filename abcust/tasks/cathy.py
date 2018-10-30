import os
from datetime import datetime
from datetime import timedelta

from awair import Awair
from awair.enums import DeviceType
from dotenv import load_dotenv

from abcust.celery import app
from abcust.tasks import slack


load_dotenv()

EMAIL = os.getenv('AWAIR_EMAIL')
PASSWORD = os.getenv('AWAIR_PASSWORD')
ACCESS_TOKEN = os.getenv('AWAIR_ACCESS_TOKEN')
DEVICE_ID = os.getenv('AWAIR_MINT_DEVICE_ID')


def get_awair():
    return Awair(email=EMAIL, password=PASSWORD, access_token=ACCESS_TOKEN)


def send_to_slack(status, message, fields=None, timestamp=None):
    slack.write.delay('cathy', status, message, fields, timestamp)


def notify_score(score):
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
    status = 'good'
    if score.score <= 80:
        status = 'bad'
    elif score.score <= 90:
        status = 'warning'
    send_to_slack(status, message, fields, score.timestamp.timestamp() + (9 * 3600)) # from utc to +09:00


@app.task
def get_score():
    score = get_awair().get_score(DeviceType.AWAIR_MINT, DEVICE_ID)
    notify_score(score)
    return score


@app.task
def get_timelines():
    start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = start_dt + timedelta(days=1)
    timelines = get_awair().get_timelines(DeviceType.AWAIR_MINT, DEVICE_ID, start_dt, end_dt)
    for timeline in timelines:
        print(timeline.timestamp)
        print(timeline.score)
    return timelines


@app.task
def get_inbox_items():
    start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = start_dt + timedelta(days=1)
    inbox_items = get_awair().get_inbox_items(start_dt, end_dt, 'ko')
    for inbox_item in inbox_items:
        print(inbox_item.timestamp)
        print(inbox_item.title)
        print(inbox_item.description)
    return inbox_items
