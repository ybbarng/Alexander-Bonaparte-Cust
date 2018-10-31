import base64
import codecs
import os

import requests

from abcust.celery import app
from abcust.tasks import slack


PAPAGO_SERVER_URL = 'https://papago.naver.com/apis/tts/'
DATA_HEADER = codecs.decode('ae55aea1439b2c557a64f8ef7069746368223a302c22737065616b6572223a226b79757269222c227370656564223a302c2274657874223a22', 'hex')
DATA_FOOTER = codecs.decode('227d', 'hex')


class TtsException(Exception):
    pass


def tidyUp(message):
    message = message.strip()
    if not message:
        return message
    if '\n' in message:
        message = message.split('\n')[0]
    return message.replace('(', '').replace(')', '.')

def getData(message):
    return base64.b64encode(DATA_HEADER + message.encode('utf-8') + DATA_FOOTER)


def createVoiceFileId(data):
    payload = {
        'data': data
    }
    r = requests.post(PAPAGO_SERVER_URL + 'makeID', data=payload)
    try:
        if r.status_code == 200:
            return r.json()['id']
        else:
            message = r.json()['message']
            raise TtsException('음성 파일의 id를 발급받지 못했습니다: {}'.format(message))
    except KeyError:
        raise TtsException('음성 파일의 id를 발급받지 못했습니다.')


def buildVoiceUrl(voiceFileId):
    return PAPAGO_SERVER_URL + voiceFileId


@app.task
def get_voice(message, play=False, share_result_to_slack=False):
    try:
        url = buildVoiceUrl(createVoiceFileId(getData(tidyUp(message))))
        if play:
            playFrom(url)
        if share_result_to_slack:
            send_to_slack_success(message, url)
    except TtsException as e:
        if share_result_to_slack:
            send_to_slack_error(message, e)
    return url


def playFrom(url):
    print('다음 파일을 재생합니다: ' + url)
    cust_fifo = '/tmp/custfifo'
    try:
        os.mkfifo(cust_fifo)
    except FileExistsError:
        pass
    command_play_from_url = '(wget "{0}" -O {1} &) && mpg321 {1}'.format(url, cust_fifo)
    os.popen(command_play_from_url, 'r')


def send_to_slack(color, message, fields):
    slack.write.delay('tts', color, message=message, fields=fields)


def send_to_slack_success(message, url):
    fields = [{
        'title': '"{}"를 음성 변환하였습니다.'.format(message),
        'value': url,
        'short': False
    }]
    send_to_slack('good', message, fields)


def send_to_slack_error(message, e):
    fields = [{
        'title': '"{}"를 음성 변환하지 못했습니다.'.format(message),
        'value': e,
        'short': False
    }]
    send_to_slack('danger', message, fields)


if __name__ == '__main__':
    while True:
        message = input('음성으로 변환할 메시지를 입력하세요: ')
        if message == 'q':
            break
        print(get_voice(message, True))
