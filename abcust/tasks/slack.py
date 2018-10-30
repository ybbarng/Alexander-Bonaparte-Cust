import json
import os

from dotenv import load_dotenv
import requests

from abcust.celery import app


load_dotenv()

WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')


@app.task
def write(name, status, message, fields=None):
    if not WEBHOOK_URL:
        raise ValueError('Invalid slack webook_url: {}'.format(WEBHOOK_URL))
    colors = {
        'good': 'good',
        'error': 'danger',
    }
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'attachments': [
            {
                'fallback': '{}: ({}) {}'.format(name, status, message),
                'title': name,
                'text': message,
                'color': colors[status],
            },
        ]
    }
    if fields:
        payload['attachments'][0]['fields'] = fields
    response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError('Request to slack returned an error: ({}, {})'.format(response.status_code, response.text))

if __name__ == '__main__':
    write('Test', 'good', 'Cust가 보낸 메시지입니다.')

