from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

bcrypt = Bcrypt()
limiter = Limiter(
    get_remote_address,
    storage_options={}
)
csrf = CSRFProtect()