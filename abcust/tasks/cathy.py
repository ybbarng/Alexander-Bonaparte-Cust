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

COLORS = ['#2EB886', '#ABA74D', '#DAA038', '#BF511C', '#A30200']


def get_awair():
    return Awair(email=EMAIL, password=PASSWORD, access_token=ACCESS_TOKEN)


def send_to_slack(color, title=None, message=None, fields=None, timestamp=None):
    slack.write.delay('Cathy', color, title, message, fields, timestamp)


def send_to_slack_blocking(color, title=None, message=None, fields=None, timestamp=None):
    slack.write('Cathy', color, title, message, fields, timestamp)


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
    color_index = 0
    if score.score <= 80:
        color_index = 4
    elif score.score <= 90:
        color_index = 2
    send_to_slack(COLORS[color_index], None, message, fields, score.timestamp.timestamp() + (9 * 3600)) # from utc to +09:00


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
def get_inbox_items(start_dt, end_dt):
    inbox_items = get_awair().get_inbox_items(start_dt, end_dt, 'ko')
    return inbox_items


@app.task
def get_inbox_items_batch(minutes=5):
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(minutes=minutes)
    inbox_items = get_inbox_items(start_dt, end_dt)
    for inbox_item in reversed(inbox_items):
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
                      fields=fields)
        return 4
