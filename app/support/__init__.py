from flask import Blueprint

support = Blueprint(
    'support', 
    __name__, 
    url_prefix='/support', 
    template_folder='templates',
    static_folder='static'
)

from . import routes
