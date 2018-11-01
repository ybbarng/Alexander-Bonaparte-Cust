import json

from abcust.celery import app
from abcust.tasks import slack


DATABASE_FILE = 'facebook_{}.json'


@app.task
def on_entry(entry):
    database = load_database(entry['name'])
    if entry['url'] in database:
        return
    slack.write.delay(
        'Facebook',
        'good',
        '\'{}\'의 새 포스트가 검색되었습니다.'.format(entry['name']),
        entry['content'],
        title_link=entry['url'])
    database.add(entry['url'])
    save_database(database, entry['name'])


def load_database(search_key):
    try:
        with open(DATABASE_FILE.format(search_key), 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return set()


def save_database(database, search_key):
    with open(DATABASE_FILE.format(search_key), 'w+') as f:
        json.dump(list(database), f)
