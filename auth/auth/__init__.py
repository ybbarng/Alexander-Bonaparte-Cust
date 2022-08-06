from flask import Flask, url_for
from flask_dance.contrib.slack import make_slack_blueprint
from werkzeug.middleware.proxy_fix import ProxyFix

from .middleware import PrefixMiddleware
from .models import db
from .routes import routes
from .settings import CLIENT_ID, CLIENT_SECRET, FLASK_SECRET_KEY


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/auth')
    app.secret_key = FLASK_SECRET_KEY

    login_blueprint = make_slack_blueprint(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=['identity.basic,identity.team'],
        redirect_url='/auth'
    )
    app.register_blueprint(login_blueprint, url_prefix='/login')
    app.register_blueprint(routes)
    return app

    @app.before_request
    def before_request():
        print('here')
        db.connect()

    @app.after_request
    def after_request(response):
        db.close()
        return response
