# A blueprint for handling requests from non-slack
from functools import wraps

from flask import abort, Blueprint, jsonify, make_response, request

from abcust.auth import authorized
from abcust.tasks import audrey
from abcust.tasks import brice
from abcust.tasks import cathy
from abcust.tasks import slack
from abcust.tasks import tts


api = Blueprint('api', __name__)


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not authorized(request):
            abort(make_response(jsonify(message="Unauthorized"), 401))
        return function(*args, **kwargs)
    return wrapper


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


@api.route('/api/test')
@login_required
def api_test():
    return jsonify({'message': 'Hello'})


@api.route('/api/audrey', methods=['POST'])
@login_required
def api_audrey():
    if request.get_json()['on']:
        audrey.turn_on()
    else:
        audrey.turn_off()
    return jsonify({'ok': True})


@api.route('/api/audrey/power', methods=['POST'])
@login_required
def api_audrey_power():
    if request.get_json()['on']:
        audrey.power_on()
    else:
        audrey.power_off()
    return jsonify({'ok': True})


@api.route('/api/audrey/raw', methods=['POST'])
@login_required
def api_audrey_raw():
    command = request.get_json()['command']
    audrey.raw(command)
    return jsonify({'ok': True})


@api.route('/api/brice/battery', methods=['GET'])
@login_required
def api_brice_battery():
    return jsonify({'ok': True, 'data': brice.get_battery()}),


@api.route('/api/brice/time', methods=['GET'])
@login_required
def api_brice_time():
    return jsonify({'ok': True, 'data': brice.get_time()}),


@api.route('/api/brice/switch/', methods=['POST'])
@api.route('/api/brice/switch/<int:switch_id>', methods=['POST'])
@login_required
def api_brice_switch(switch_id=None):
    turn_on = request.get_json()['on']
    if switch_id:
        if turn_on:
            brice.turn_on(switch_id)
        else:
            brice.turn_off(switch_id)
    else:
        if turn_on:
            brice.turn_on_all()
        else:
            brice.turn_off_all()
    return jsonify({'ok': True})


@api.route('/api/cathy/', methods=['GET'])
@login_required
def api_cathy():
    score = cathy.get_score()
    response = {
        'total_score': {
            'score': score.score,
            'color': cathy.get_color_of_total_score(score.score)
        },
        'temperature': {
            'score': score.sensor.temp,
            'color': score.index.temp
        },
        'humidity': {
            'score': score.sensor.humidity,
            'color': score.index.humidity
        },
        'voc': {
            'score': score.sensor.voc,
            'color': score.index.voc
        },
        'pm25': {
            'score': score.sensor.pm25,
            'color': score.index.pm25
        },
    }
    return jsonify({'ok': True, 'data': response})
