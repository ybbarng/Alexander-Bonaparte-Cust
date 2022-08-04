from base64 import b64decode
import os

from dotenv import load_dotenv


load_dotenv()


AUDREY_MAC_ADDRESS = os.getenv('AUDREY_MAC_ADDRESS')
AUTH_AEAD_SECRET = b64decode(os.getenv('AUTH_AEAD_SECRET_B64'))
AWAIR_ACCESS_TOKEN = os.getenv('AWAIR_ACCESS_TOKEN')
AWAIR_DEVICE_ID = os.getenv('AWAIR_MINT_DEVICE_ID')
AWAIR_EMAIL = os.getenv('AWAIR_EMAIL')
AWAIR_PASSWORD = os.getenv('AWAIR_PASSWORD')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
FLASK_SECRET_KEY = bytes.fromhex(os.getenv('FLASK_SECRET_KEY_HEX'))
REDIS_URL = os.getenv('REDIS_URL')
SLACK_LOG_URL = os.getenv('SLACK_LOG_URL')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
SWITCHER_MAC_ADDRESS = os.getenv('SWITCHER_MAC_ADDRESS')
SWITCHER_SHARE_CODE = os.getenv('SWITCHER_SHARE_CODE')
