import os

from dotenv import load_dotenv
from flask import Flask
from flask_dance.contrib.slack import make_slack_blueprint, slack

from abcust.blueprints.api import api
from abcust.blueprints.remote_controller import remote_controller
from abcust.blueprints.slack import slack
from abcust.middleware import PrefixMiddleware


load_dotenv()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/cust')
    app.secret_key = bytes.fromhex(os.getenv('FLASK_SECRET_KEY_HEX'))

    app.register_blueprint(api)
    app.register_blueprint(make_slack_blueprint())
    app.register_blueprint(slack)
    app.register_blueprint(remote_controller)
    return app
