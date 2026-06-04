from flask import Blueprint

hr = Blueprint('hr', __name__, static_folder='static', static_url_path='/hr_static', template_folder='templates', url_prefix='')

from . import routes  # noqa: F401, E402
