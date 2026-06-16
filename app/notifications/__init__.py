from flask import Blueprint

notifications = Blueprint(
    'notifications',
    __name__,
    static_folder='static',
    static_url_path='/notifications_static',
    template_folder='templates',
    url_prefix='/notifications'
)

from . import routes
