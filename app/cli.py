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

    @app.cli.command('update-user-role')
    @click.argument('email')
    @click.argument('role_name')
    def update_user_role(email, role_name):
        """Update a user's role by email.

        Example usage:
          flask update-user-role user@example.com admin
        """
        from app.models import User, Role
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f'[ERROR] No user found with email: {email}')
                return
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                print(f'[ERROR] No role found with name: {role_name}')
                return
            user.role = role
            db.session.commit()
            print(f'[OK] Updated role for user {email} to {role_name}.')

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
        from flask_migrate import migrate as fm_migrate
        try:
            # revision is present in some flask_migrate versions
            from flask_migrate import revision as fm_revision
        except Exception:
            fm_revision = None

        try:
            from flask_migrate import upgrade as fm_upgrade
        except Exception:
            fm_upgrade = None

        with app.app_context():
            if autogenerate:
                fm_migrate(message=message)
                print(f"[OK] Migration generated: '{message}' (autogenerate=True)")
            else:
                # try to create an empty revision (no autogenerate) if supported
                if fm_revision:
                    try:
                        fm_revision(message=message, autogenerate=False)
                    except TypeError:
                        # some versions don't accept autogenerate kwarg
                        fm_revision(message=message)
                    print(f"[OK] Empty migration (no-autogenerate) generated: '{message}'")
                else:
                    # fallback to migrate (may autogenerate depending on version)
                    fm_migrate(message=message)
                    print(f"[OK] Migration generated: '{message}' (autogenerate flag ignored)")

            if upgrade:
                if fm_upgrade:
                    fm_upgrade()
                    print('[OK] Database upgraded to latest revision.')
                else:
                    print('[WARN] Upgrade function not available in flask_migrate; skipping upgrade.')

    @app.cli.command('bootstrap-db')
    @click.option('--stamp-head/--no-stamp', default=True, help='Stamp the DB with current head after creating tables')
    def bootstrap_db(stamp_head):
        """Create database tables from current models and optionally stamp Alembic head.

        Use this when initializing a fresh database that predates Alembic migrations.
        """
        from app import create_app
        from app.models import db as models_db
        from flask_migrate import stamp as fm_stamp

        # create tables from models
        with app.app_context():
            models_db.create_all()
            print('[OK] Database tables created from current models.')
            if stamp_head:
                try:
                    fm_stamp(revision='head')
                    print('[OK] Alembic stamped to head.')
                except Exception as e:
                    print('[WARN] Could not stamp Alembic head:', e)
