from app import create_app
from app.models import db, Role, Permission
from app.middleware.rbac import seed_default_roles_and_permissions

app = create_app()

with app.app_context():
    seed_default_roles_and_permissions(db, Role, Permission)
    print("RBAC roles and permissions updated successfully.")
