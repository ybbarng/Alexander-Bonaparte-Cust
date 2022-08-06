from datetime import datetime

from abcust.celery import app
from abcust.tasks import audrey
from abcust.tasks import cathy
from abcust.tasks import slack


@app.task
def get_awair_inbox_items():
    return cathy.get_inbox_items_batch()

def get_cold_threshold():
    SUMMER_COLD_THRESHOLD = 22
    ELSE_COLD_THRESHOLD = -100  # 이 기능 사용하지 않음
    if 5 < datetime.now().month < 9:
        return SUMMER_COLD_THRESHOLD
    else:
        return ELSE_COLD_THRESHOLD

# @app.task
def turn_off_aircon_when_cold():
    cold_threshold = get_cold_threshold()
    score = cathy.get_score()
    if score is None:
        return
    if score.sensor.temp <= cold_threshold:
        audrey.turn_off.delay()
        message = '너무 춥네요. 혹시 에어컨이 켜져 있으면 끌게요.'
        slack.write.delay('A. B. Cust', 'danger', message=message, log=True)
