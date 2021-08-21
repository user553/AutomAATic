from flask import Blueprint, render_template
from flask_login import login_required

index_bp = Blueprint('index_bp', __name__, static_folder='resources')


# reference. 22 March https://stackoverflow.com/questions/13428708/best-way-to-make-flask-logins-login-required-the-default/25804147#25804147
# Make login required for all endpoints within blueprint
@index_bp.before_request
@login_required
def before_request():
    pass


@index_bp.route('/home')
@index_bp.route('/')
def home():
    return render_template('index.html')


@index_bp.route('/echarts/')
def echarts():
    return render_template('echarts.html')
