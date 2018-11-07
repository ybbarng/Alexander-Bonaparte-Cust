# A blueprint for handling requests from non-slack

from flask import abort, Blueprint, jsonify, request

from abcust.tasks import audrey
from abcust.tasks import brice
from abcust.tasks import slack
from abcust.tasks import tts


api = Blueprint('api', __name__)


@api.route('/')
def main():
    return 'Hello, It\'s Alexander Bonaparte Cust.'


@api.route('/tts', methods=['POST'])
def on_tts():
    service = request.form['service']
    message = request.form['text']

    tts.get_voice.delay('{} {}'.format(service, message), True)

    slack.write.delay('tts', 'good', message=message, log=False)

    response = {}
    return jsonify(response)
