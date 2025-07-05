from flask import Blueprint

dashboard = Blueprint('dashboard', __name__, static_folder='static', static_url_path='/dashboard_static', template_folder='templates', url_prefix='')

from . import routes