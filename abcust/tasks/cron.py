from abcust.celery import app
from abcust.tasks import audrey
from abcust.tasks import cathy
from abcust.tasks import slack


@app.task
def get_awair_inbox_items():
    return cathy.get_inbox_items_batch()


@app.task
def turn_off_aircon_when_cold():
    COLD_THRESHOLD = 22
    score = cathy.get_score()
    if score.sensor.temp <= COLD_THRESHOLD:
        audrey.turn_off.delay()
        message = '너무 춥네요. 혹시 에어컨이 켜져 있으면 끌게요.'
        slack.write.delay('A. B. Cust', 'danger', message=message, log=True)
