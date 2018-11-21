from datetime import datetime
from functools import wraps
import json

from abcust.celery import app
from abcust.lib.switcher import Switcher
from abcust.settings import SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE
from abcust.tasks import slack


CACHE_FILE = 'brice_cache.json'


def notify(message, log=True):
    slack.write.delay('Brice', 'good', message=message, log=log)


def manage_switch(switch_index, on=True):
    if switch_index not in [1, 2]:
        raise ValueError('잘못된 조명 번호입니다: {}'.format(switch_index))
    switcher = Switcher(SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE)
    switcher.manage_switch(switch_index, on)
    switcher.disconnect()
    notify('{}번 조명을 {}습니다.'.format(switch_index, '켰' if on else '껐'))


def manage_switch_all(on=True):
    switcher = Switcher(SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE)
    for switch_index in [1, 2]:
        switcher.manage_switch(switch_index, on)
    switcher.disconnect()
    notify('모든 조명을 {}습니다.'.format('켰' if on else '껐'))


@app.task
def turn_on(switch_index):
    manage_switch(switch_index, True)


@app.task
def turn_off(switch_index):
    manage_switch(switch_index, False)


@app.task
def turn_on_all():
    manage_switch_all(True)


@app.task
def turn_off_all():
    manage_switch_all(False)


def load_data_from_cache(key):
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
    except:
        return None
    if datetime.fromtimestamp(data[key]['expired_at']) <= datetime.utcnow():
        return None
    return data[key]['value']


def load_battery_from_cache():
    return load_data_from_cache('battery')


def load_time_from_cache():
    return load_data_from_cache('time')


def save_data_to_cache(key, value):
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
    except:
        data = {}
    key_data = {
        'expired_at': datetime.utcnow().timestamp() + 24 * 60 * 60,
        'value': value
    }
    data[key] = key_data
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)


def save_battery_to_cache(battery):
    save_data_to_cache('battery', battery)


def save_time_to_cache(time):
    save_data_to_cache('time', time)


def get_battery():
    battery = load_battery_from_cache()
    if battery:
        return battery
    switcher = Switcher(SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE)
    battery = switcher.get_battery()
    switcher.disconnect()
    save_battery_to_cache(battery)
    return battery


@app.task
def notify_battery():
    battery = get_battery()
    notify('배터리가 {}% 남았습니다.'.format(battery), log=False)
    return battery


@app.task
def get_time():
    time = load_time_from_cache()
    if time:
        return time
    switcher = Switcher(SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE)
    time = switcher.get_time()
    switcher.disconnect()
    save_time_to_cache(time)
    notify('현재 시간이 \'{}\'으로 설정되어 있습니다.'.format(time), log=False)
    return time
