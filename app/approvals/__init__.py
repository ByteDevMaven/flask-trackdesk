from flask import Blueprint

approvals_bp = Blueprint('approvals', __name__, template_folder='templates')

from . import routes
