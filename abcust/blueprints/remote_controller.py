# A blueprint for remote conroller web interface
from urllib.parse import quote
from flask import Blueprint, redirect, url_for, render_template
from abcust.auth import authorized


remote_controller = Blueprint('remote_controller', __name__)

@remote_controller.route('/remote-controller')
def index():
    if not authorized():
        return redirect('/auth?from={}'.format(quote(url_for('remote_controller.index'))))
    return render_template('remote-controller.html')
