from functools import wraps
from flask import abort
from flask_login import current_user

def require_permission(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            role = current_user.role  # Assuming `role_id` is set and relationship exists
            if not role:
                abort(403)  # Forbidden
            
            # Check if any of the role's permissions match the required one
            has_permission = any(p.name == permission_name for p in role.permissions)

            if not has_permission:
                abort(403)  # Forbidden

            return f(*args, **kwargs)
        return decorated_function
    return decorator
