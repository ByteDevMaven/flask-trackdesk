from flask import Blueprint

auth = Blueprint('auth', __name__, static_folder='static', static_url_path='/auth_static', template_folder='templates', url_prefix='')

from . import routes