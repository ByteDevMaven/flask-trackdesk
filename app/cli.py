from flask import Flask
from app.extensions import db

def register_cli(app: Flask):
    @app.cli.command('seed-rbac')
    def seed_rbac():
        """Seed default roles and permissions into the database.

        Run with:  flask seed-rbac
        """
        from app.middleware.rbac import seed_default_roles_and_permissions
        from app.models import Role, Permission
        with app.app_context():
            seed_default_roles_and_permissions(db, Role, Permission)
        print('[OK] RBAC roles and permissions seeded successfully.')
