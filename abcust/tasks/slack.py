import json
import os

from dotenv import load_dotenv
import requests

from abcust.celery import app


load_dotenv()

WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')


@app.task
def write(name, color, title=None, message=None, fields=None, timestamp=None):
    # color: good(#2EB886), warning(#DAA038), danger(#A30200), #439FE0
    if not WEBHOOK_URL:
        raise ValueError('Invalid slack webook_url: {}'.format(WEBHOOK_URL))
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'attachments': [
            {
                'author_name': name,
                'fallback': '{}: ({}) {}'.format(name, color, message),
                'text': message,
                'color': color,
            },
        ]
    }
    if title:
        payload['attachments'][0]['title'] = title

    if fields:
        payload['attachments'][0]['fields'] = fields

    if timestamp:
        payload['attachments'][0]['ts'] = timestamp

    response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError('Request to slack returned an error: ({}, {})'.format(response.status_code, response.text))

if __name__ == '__main__':
    write('Cust', 'good', 'Test', 'Cust가 보낸 메시지입니다.')

