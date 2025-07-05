from flask import Blueprint

payments = Blueprint('payments', __name__, static_folder='static', static_url_path='/payments_static', template_folder='templates', url_prefix='')

from . import routes