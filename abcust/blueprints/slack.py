# A blueprint for slack actions

from flask import abort, Blueprint, jsonify, request

from abcust.tasks import audrey
from abcust.tasks import brice
from abcust.tasks import cathy
from abcust.tasks import tts


slack = Blueprint('slack', __name__)


@slack.route('/slack', methods=['POST'])
def on_slack():
    command = request.form['command'][1:]
    action = None
    if 'audrey' in command:
        action = action_audrey
    elif 'brice' in command:
        action = action_brice
    elif 'cathy' in command:
        action = action_cathy
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


def action_cathy(request):
    command = request.form['command'].replace('/', '')
    my_actions = {
        'cathy_score': cathy.get_score,
    }
    my_actions[command].delay()
    response = {
        'response_type': 'in_channel',
        'text': 'Cathy에게 명령을 전달했습니다.',
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
