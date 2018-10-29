import os

from celery import Celery
from dotenv import load_dotenv

import celeryconfig
from lib.audrey import Audrey
import slack


load_dotenv()

AUDREY_MAC_ADDRESS = os.getenv('AUDREY_MAC_ADDRESS')

app = Celery('audrey', config_source=celeryconfig)


def notify(message):
    slack.write.delay('Audrey', 'good', message)


@app.task()
def power_on():
    audrey = Audrey(AUDREY_MAC_ADDRESS, debug=True)
    audrey.send_command('TOGGLE:POWER:ON')
    audrey.disconnect()
    notify('파워모드를 켰습니다.')


@app.task()
def power_off():
    audrey = Audrey(AUDREY_MAC_ADDRESS, debug=True)
    audrey.send_command('NORMAL:COOL:27:LOW')
    audrey.disconnect()
    notify('파워모드를 껐습니다.')


@app.task()
def raw_command(command):
    audrey = Audrey(AUDREY_MAC_ADDRESS, debug=True)
    audrey.send_command(command)
    audrey.disconnect()
    notify('다음 명령을 받았습니다: {}'.format(command))
