from flask import Flask
from app.extensions import db
import click

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

    @app.cli.command('migrate-db')
    @click.option('-m', '--message', default='Auto migration', help='Migration message')
    @click.option('--autogenerate/--no-autogenerate', default=True, help='Autogenerate migration')
    @click.option('--upgrade/--no-upgrade', default=False, help='Run db upgrade after migrate')
    def migrate_db(message, autogenerate, upgrade):
        """Create a migration script (and optionally upgrade DB).

        Examples:
          flask migrate-db -m "Add new column"
          flask migrate-db --no-autogenerate --upgrade
        """
        from flask_migrate import migrate as fm_migrate, upgrade as fm_upgrade
        with app.app_context():
            fm_migrate(message=message, autogenerate=autogenerate)
            print(f"[OK] Migration generated: '{message}' (autogenerate={autogenerate})")
            if upgrade:
                fm_upgrade()
                print('[OK] Database upgraded to latest revision.')
