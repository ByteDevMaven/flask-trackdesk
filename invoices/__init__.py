from flask import Blueprint

invoices = Blueprint('invoices', __name__, static_folder='static', static_url_path='/invoices_static', template_folder='templates', url_prefix='')

from . import routes