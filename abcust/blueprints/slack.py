# A blueprint for slack actions
from functools import wraps
import hmac
import hashlib
import os
from time import time

from dotenv import load_dotenv
from flask import abort, Blueprint, jsonify, make_response, request

from abcust.tasks import audrey
from abcust.tasks import brice
from abcust.tasks import cathy
from abcust.tasks import tts


load_dotenv()
signed_secret = os.getenv('SLACK_SIGNING_SECRET')


slack = Blueprint('slack', __name__)


def verify_slack_request(signed_secret):
    def verify_slack_request_decorator(f):
        def is_old(request):
            # The request timestamp is more than five minutes from local time.
            # It could be a replay attack, so let's ignore it.
            request_timestamp = request.headers['X-Slack-Request-Timestamp']
            return abs(time() - int(request_timestamp)) > 60 * 5

        def verify_signature(request):
            version = 'v0'
            request_timestamp = request.headers['X-Slack-Request-Timestamp']
            signature = request.headers['X-Slack-Signature']
            body = request.get_data()
            base_string = ':'.join([version, request_timestamp, body.decode('utf-8')])
            calculated_hash = version + '=' + hmac.new(
                signed_secret.encode('utf-8'),
                base_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            # compare with compare_digest() to avoid timing attack
            return hmac.compare_digest(calculated_hash, signature)

        @wraps(f)
        def function_wrapper(*args, **kwargs):
            if is_old(request):
                return make_response("", 403)

            if not verify_signature(request):
                return make_response("", 403)

            return f(*args, **kwargs)

        return function_wrapper
    return verify_slack_request_decorator


@slack.route('/slack', methods=['POST'])
@verify_slack_request(signed_secret)
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
    elif 'ping' == command:
        action = action_ping
    if action is None:
        return abort(400)
    return action(request)


def action_audrey(request):
    my_actions = {
        'audrey_power_on': audrey.power_on,
        'audrey_power_off': audrey.power_off,
        'audrey_turn_on': audrey.turn_on,
        'audrey_turn_off': audrey.turn_off,
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
    if 'turn' in command and 'all' not in command:
        switch = int(request.form['text'])
        if 'on' in command:
            brice.turn_on.delay(switch)
        else:
            brice.turn_off.delay(switch)
    else:
        my_actions = {
            'brice_battery': brice.get_battery,
            'brice_time': brice.get_time,
            'brice_turn_on_all': brice.turn_on_all,
            'brice_turn_off_all': brice.turn_off_all,
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
        'cathy_score': cathy.notify_score,
    }
    my_actions[command].delay()
    response = {
        'response_type': 'in_channel',
        'text': 'Cathy에게 명령을 전달했습니다.',
    }
    return jsonify(response)


def action_tts(request):
    message = request.form['text']
    tts.get_voice.delay(message, False, True)
    response = {
        'response_type': 'in_channel',
        'text': '"{}"의 음성 변환을 시도합니다.'.format(message),
    }
    return jsonify(response)


def action_ping(request):
    return 'pong'
