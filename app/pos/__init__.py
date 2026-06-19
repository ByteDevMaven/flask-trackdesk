from flask import Blueprint

pos = Blueprint("pos", __name__, template_folder="templates", static_folder="static", static_url_path='/pos_static')

from . import routes  # noqa: E402,F401
