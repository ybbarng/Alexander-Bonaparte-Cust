import os

from celery import Celery
from dotenv import load_dotenv


load_dotenv()


imports = ('abcust.tasks.audrey', 'abcust.tasks.brice', 'abcust.tasks.slack', 'abcust.tasks.tts')
broker_url = os.getenv('BROKER_URL')
result_backend = os.getenv('CELERY_RESULT_BACKEND')


app = Celery('abcust',
             broker=broker_url,
             backend=result_backend,
             include=imports)


if __name__ == '__main__':
    app.start()
