import os

from dotenv import load_dotenv


load_dotenv()


imports = ('audrey', 'brice', 'slack', 'tts')
broker_url = os.getenv('BROKER_URL')
result_backend = os.getenv('CELERY_RESULT_BACKEND')
