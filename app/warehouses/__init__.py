from flask import Blueprint

warehouses = Blueprint('warehouses', __name__, static_folder='static', static_url_path='/warehouses_static', template_folder='templates', url_prefix='')

from . import routes
