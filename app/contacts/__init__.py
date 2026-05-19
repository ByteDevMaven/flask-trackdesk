from flask import Blueprint

contacts = Blueprint('contacts', __name__, template_folder='templates')

from . import routes
