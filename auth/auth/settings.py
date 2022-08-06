import os

from dotenv import load_dotenv

load_dotenv()


CLIENT_ID = os.getenv('SLACK_CREDENTIAL_CLIENT_ID')
CLIENT_SECRET = os.getenv('SLACK_CREDENTIAL_CLIENT_SECRET')
FLASK_SECRET_KEY = bytes.fromhex(os.getenv('FLASK_SECRET_KEY_HEX'))
SLACK_TEAM_NAME = os.getenv('SLACK_TEAM_NAME')
SLACK_TEAM_ID = os.getenv('SLACK_TEAM_ID')
SIPHASH_KEY = bytes.fromhex(os.getenv('SIPHASH_KEY_HEX'))
JWT_KEY = bytes.fromhex(os.getenv('JWT_KEY_HEX'))
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
