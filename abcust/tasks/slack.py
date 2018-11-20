import json

import requests

from abcust.celery import app
from abcust.settings import SLACK_WEBHOOK_URL, SLACK_LOG_URL


@app.task
def write(name, color, title=None, message=None, fields=None, timestamp=None, title_link=None, log=True):
    # color: good(#2EB886), warning(#DAA038), danger(#A30200), #439FE0
    url = SLACK_LOG_URL if log else SLACK_WEBHOOK_URL
    if not url:
        raise ValueError('Invalid slack webook_url: {}'.format(url))
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

    if title_link:
        payload['attachments'][0]['title_link'] = title_link

    if fields:
        payload['attachments'][0]['fields'] = fields

    if timestamp:
        payload['attachments'][0]['ts'] = timestamp

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise ValueError('Request to slack returned an error: ({}, {})'.format(response.status_code, response.text))

if __name__ == '__main__':
    write('Cust', 'good', 'Test', 'Cust가 보낸 메시지입니다.')

