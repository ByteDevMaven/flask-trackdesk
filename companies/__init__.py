from flask import Blueprint

companies = Blueprint('companies', __name__, static_folder='static', static_url_path='/companies_static', template_folder='templates', url_prefix='')

from . import routes