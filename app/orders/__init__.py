from flask import Blueprint

orders = Blueprint('orders', __name__, static_folder='static', static_url_path='/orders_static', template_folder='templates', url_prefix='')

from . import routes