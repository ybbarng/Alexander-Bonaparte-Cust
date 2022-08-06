import os

from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
DEFAULT_REPLY = os.getenv('DEFAULT_REPLY')
