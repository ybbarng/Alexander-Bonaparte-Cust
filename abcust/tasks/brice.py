from functools import wraps

from abcust.celery import app
from abcust.lib.switcher import Switcher
from abcust.settings import SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE
from abcust.tasks import slack


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


@app.task
def get_battery():
    switcher = Switcher(SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE)
    battery = switcher.get_battery()
    switcher.disconnect()
    notify('배터리가 {}% 남았습니다.'.format(battery), log=False)
    return battery


@app.task
def get_time():
    switcher = Switcher(SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE)
    time = switcher.get_time()
    switcher.disconnect()
    notify('현재 시간이 \'{}\'으로 설정되어 있습니다.'.format(time), log=False)
    return time
