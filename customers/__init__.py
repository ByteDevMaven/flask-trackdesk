from flask import Blueprint

customers = Blueprint('customers', __name__, static_folder='static', static_url_path='/customers_static', template_folder='templates', url_prefix='')

from . import routes