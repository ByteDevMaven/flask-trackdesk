from flask import Blueprint

inventory = Blueprint('inventory', __name__, static_folder='static', static_url_path='/inventory_static', template_folder='templates', url_prefix='')

from . import routes