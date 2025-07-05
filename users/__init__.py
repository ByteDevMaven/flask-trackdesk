from flask import Blueprint

users = Blueprint('users', __name__, static_folder='static', static_url_path='/users_static', template_folder='templates', url_prefix='')

from . import routes