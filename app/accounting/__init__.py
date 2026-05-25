from flask import Blueprint

accounting = Blueprint('accounting', __name__, static_folder='static', static_url_path='/accounting_static', template_folder='templates', url_prefix='')

from . import routes
