from flask import Blueprint

suppliers = Blueprint('suppliers', __name__, static_folder='static', static_url_path='/suppliers_static', template_folder='templates', url_prefix='')

from . import routes