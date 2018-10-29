# A web server for slack actions

import os

from dotenv import load_dotenv
from flask import abort, Flask, jsonify, request

import audrey
import brice
import slack
import tts


load_dotenv()

AUDREY_MAC_ADDRESS = os.getenv('AUDREY_MAC_ADDRESS')


app = Flask(__name__)


@app.route('/')
def main():
    return 'Hello, It\'s Alexander Bonaparte Cust.'


@app.route('/slack', methods=['POST'])
def slack():
    command = request.form['command'][1:]
    action = None
    if 'audrey' in command:
        action = action_audrey
    elif 'brice' in command:
        action = action_brice
    elif 'tts' == command:
        action = action_tts
    if action is None:
        return abort(400)
    return action(request)


def action_audrey(request):
    my_actions = {
        'audrey_power_on': audrey.power_on,
        'audrey_power_off': audrey.power_off,
    }
    command = request.form['command'].replace('/', '')
    if command == 'audrey_raw':
        audrey.raw_command.delay(request.form['text'])
    else:
        my_actions[command].delay()
    response = {
        'response_type': 'in_channel',
        'text': 'Audrey에게 명령을 전달했습니다.',
    }
    return jsonify(response)


def action_brice(request):
    command = request.form['command'].replace('/', '')
    if 'turn' in request.form['command']:
        switch = int(request.form['text'])
        if 'on' in command:
            brice.turn_on.delay(switch)
        else:
            brice.turn_off.delay(switch)
    else:
        my_actions = {
            'brice_battery': brice.get_battery,
            'brice_time': brice.get_time,
        }
        my_actions[command].delay()
    response = {
        'response_type': 'in_channel',
        'text': 'Brice에게 명령을 전달했습니다.',
    }
    return jsonify(response)


def action_tts(request):
    message = request.form['text']
    tts.getVoice.delay(message, False, True)
    response = {
        'response_type': 'in_channel',
        'text': '"{}"의 음성 변환을 시도합니다.'.format(message),
    }
    return jsonify(response)


@app.route('/tts', methods=['POST'])
def on_tts():
    service = request.form['service']
    message = request.form['text']

    tts.getVoice.delay('{} {}'.format(service, message), True)

    slack_status = 'good'
    slack_message = message
    slack.write.delay('tts', slack_status, slack_message)

    response = {}
    return jsonify(response)


def run(port=None):
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run(8000)
