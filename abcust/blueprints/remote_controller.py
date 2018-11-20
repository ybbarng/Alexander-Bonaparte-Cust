# A blueprint for remote conroller web interface
from urllib.parse import quote
from flask import Blueprint, redirect, url_for, render_template, request, session
from abcust.auth import access_token_issued, authorized


remote_controller = Blueprint('remote_controller', __name__)

@remote_controller.route('/remote-controller')
def index():
    has_token = access_token_issued(request)
    if has_token:
        return redirect(url_for('remote_controller.index'))
    if not authorized(request):
        return redirect('/auth?from={}'.format(quote(url_for('remote_controller.index'))))
    return render_template('remote-controller.html')
