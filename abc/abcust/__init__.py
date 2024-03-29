from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from abcust.blueprints.api import api
from abcust.blueprints.remote_controller import remote_controller
from abcust.blueprints.slack import slack
from abcust.settings import FLASK_SECRET_KEY
from abcust.middleware import PrefixMiddleware


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/abc')
    app.secret_key = FLASK_SECRET_KEY

    app.register_blueprint(api)
    app.register_blueprint(slack)
    app.register_blueprint(remote_controller)
    return app
