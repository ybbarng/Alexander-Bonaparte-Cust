import json

from abcust.celery import app
from abcust.tasks import slack
import mmh3


DATABASE_FILE = 'facebook_{}.json'


@app.task
def on_entry(entry):
    database = load_database(entry['name'])
    hash_key = mmh3.hash(entry['content'][:20])
    if hash_key in database:
        return
    message = '\'{}\'의 새 포스트가 검색되었습니다.'.format(entry['name'])
    print(message)
    slack.write.delay(
        'Facebook',
        'good',
        message,
        entry['content'],
        title_link=entry['url'])
    database.add(hash_key)
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
