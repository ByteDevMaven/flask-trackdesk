"""
RBAC Middleware
===============
Plugged into the app via ``init_rbac(app)`` in ``app/__init__.py``.

How it works
------------
* A ``ROUTE_PERMISSIONS`` map declares which blueprint.endpoint requires which
  permission string.  Permission strings follow the convention
  ``<blueprint>.<action>`` (e.g. ``users.manage``, ``inventory.view``).
* On every request ``before_request`` checks whether the resolved endpoint
  requires a permission.  If it does, the current user must carry that
  permission through their role; otherwise a 403 is returned.
* Public / auth routes and static assets are always allowed through.

Adding a new protected route
-----------------------------
Just add an entry to ``ROUTE_PERMISSIONS``:

    'blueprint_name.endpoint_name': 'some_blueprint.some_action',

Roles / permissions are stored in the database so you can seed them once and
update them without touching this file (see seed helper below).
"""

from flask import Flask, abort, request
from flask_login import current_user

# ---------------------------------------------------------------------------
# Permission map  –  'blueprint.endpoint' -> 'required permission string'
# ---------------------------------------------------------------------------
# Convention: permission strings are '<resource>.<action>' where action is
#   view   – read-only access
#   manage – create / update (implies view)
#   delete – destructive operations (implies manage)
#   admin  – full control incl. configuration (implies delete)
#
# Roles are seeded separately (see seed_default_roles_and_permissions).
# ---------------------------------------------------------------------------

ROUTE_PERMISSIONS: dict[str, str] = {
    # ── Dashboard ──────────────────────────────────────────────────────────
    'dashboard.index': 'dashboard.view',

    # ── Contacts ──────────────────────────────────────────────────────────
    'contacts.index':  'contacts.view',
    'contacts.view':   'contacts.view',
    'contacts.create': 'contacts.manage',
    'contacts.store':  'contacts.manage',
    'contacts.edit':   'contacts.manage',
    'contacts.update': 'contacts.manage',
    'contacts.delete': 'contacts.delete',

    # ── Inventory ─────────────────────────────────────────────────────────
    'inventory.index':  'inventory.view',
    'inventory.view':   'inventory.view',
    'inventory.create': 'inventory.manage',
    'inventory.store':  'inventory.manage',
    'inventory.edit':   'inventory.manage',
    'inventory.update': 'inventory.manage',
    'inventory.delete': 'inventory.delete',

    # ── Orders ────────────────────────────────────────────────────────────
    'orders.index':  'orders.view',
    'orders.view':   'orders.view',
    'orders.create': 'orders.manage',
    'orders.store':  'orders.manage',
    'orders.edit':   'orders.manage',
    'orders.update': 'orders.manage',
    'orders.delete': 'orders.delete',

    # ── Invoices ──────────────────────────────────────────────────────────
    'invoices.index':  'invoices.view',
    'invoices.view':   'invoices.view',
    'invoices.create': 'invoices.manage',
    'invoices.store':  'invoices.manage',
    'invoices.edit':   'invoices.manage',
    'invoices.update': 'invoices.manage',
    'invoices.delete': 'invoices.delete',

    # ── Payments ──────────────────────────────────────────────────────────
    'payments.index':  'payments.view',
    'payments.view':   'payments.view',
    'payments.create': 'payments.manage',
    'payments.store':  'payments.manage',
    'payments.edit':   'payments.manage',
    'payments.update': 'payments.manage',
    'payments.delete': 'payments.delete',

    # ── Companies ─────────────────────────────────────────────────────────
    'companies.index':  'companies.view',
    'companies.view':   'companies.view',
    'companies.create': 'companies.manage',
    'companies.store':  'companies.manage',
    'companies.edit':   'companies.manage',
    'companies.update': 'companies.manage',
    'companies.delete': 'companies.admin',

    # ── Users (admin-only) ────────────────────────────────────────────────
    'users.index':              'users.view',
    'users.view':               'users.view',
    'users.create':             'users.manage',
    'users.store':              'users.manage',
    'users.edit':               'users.manage',
    'users.update':             'users.manage',
    'users.delete':             'users.admin',
    'users.toggle_status':      'users.manage',
    'users.send_password_reset':'users.admin',
    'users.search':             'users.view',

    # ── Accounting ────────────────────────────────────────────────────────
    'accounting.index':                     'accounting.view',
    'accounting.ledger':                    'accounting.view',
    'accounting.chart_of_accounts':         'accounting.view',
    'accounting.create_expense':            'accounting.manage',
    'accounting.create_project':            'accounting.manage',
    'accounting.create_account':            'accounting.manage',
    'accounting.generate_default_accounts': 'accounting.manage',

    # ── Global search ─────────────────────────────────────────────────────
    'search': 'dashboard.view',
}

# Endpoints that are always public (no login / permission required).
PUBLIC_ENDPOINTS: frozenset[str] = frozenset({
    'auth.login',
    'auth.logout',
    'auth.register',
    'auth.forgot_password',
    'auth.reset_password',
    'static',
    'set_company',
    'set_language',
})


def init_rbac(app: Flask) -> None:
    """Register the RBAC ``before_request`` hook on *app*."""

    @app.before_request
    def enforce_rbac():
        endpoint = request.endpoint

        # No matched route (404 etc.) or always-public endpoint → skip.
        if not endpoint or endpoint in PUBLIC_ENDPOINTS:
            return

        required_permission = ROUTE_PERMISSIONS.get(endpoint)

        # Route not listed in the map → no permission required.
        if required_permission is None:
            return

        # Unauthenticated users are handled by Flask-Login's @login_required;
        # we let it do its job (redirect to login page).
        if not current_user.is_authenticated:
            return

        if not current_user.has_permission(required_permission):
            abort(403)


# ---------------------------------------------------------------------------
# Seed helper  –  call once (e.g. via a CLI command or migration)
# ---------------------------------------------------------------------------

def seed_default_roles_and_permissions(db, Role, Permission):
    """
    Seed the database with default roles and their permissions.

    Roles
    -----
    admin      – full access to everything
    manager    – manage (create/edit) most resources, no user admin
    accountant – view + manage invoices/payments, view everything else
    viewer     – read-only access to all resources

    Call this from a Flask CLI command, for example::

        @app.cli.command('seed-rbac')
        def seed_rbac():
            from app.middleware.rbac import seed_default_roles_and_permissions
            from app.models import db, Role, Permission
            seed_default_roles_and_permissions(db, Role, Permission)
            print('Done.')
    """

    # Collect every unique permission string from the map.
    all_permission_names: set[str] = set(ROUTE_PERMISSIONS.values())

    # Ensure Permission rows exist.
    permission_objs: dict[str, Permission] = {}
    for perm_name in all_permission_names:
        obj = Permission.query.filter_by(name=perm_name).first()
        if not obj:
            obj = Permission(name=perm_name)
            db.session.add(obj)
        permission_objs[perm_name] = obj

    db.session.flush()

    def _perms(*names: str) -> list:
        return [permission_objs[n] for n in names if n in permission_objs]

    # ── Role definitions ───────────────────────────────────────────────────
    role_definitions: dict[str, list[str]] = {
        'admin': list(all_permission_names),        # everything

        'manager': [
            'dashboard.view',
            'contacts.view',   'contacts.manage',   'contacts.delete',
            'inventory.view',  'inventory.manage',  'inventory.delete',
            'orders.view',     'orders.manage',     'orders.delete',
            'invoices.view',   'invoices.manage',   'invoices.delete',
            'payments.view',   'payments.manage',   'payments.delete',
            'companies.view',  'companies.manage',
            'users.view',
            'accounting.view', 'accounting.manage',
        ],

        'accountant': [
            'dashboard.view',
            'contacts.view',
            'inventory.view',
            'orders.view',
            'invoices.view',   'invoices.manage',
            'payments.view',   'payments.manage',
            'companies.view',
            'users.view',
            'accounting.view', 'accounting.manage',
        ],

        'viewer': [
            'dashboard.view',
            'contacts.view',
            'inventory.view',
            'orders.view',
            'invoices.view',
            'payments.view',
            'companies.view',
            'users.view',
            'accounting.view',
        ],
    }

    for role_name, perm_names in role_definitions.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)

        # Assign only permissions that exist in permission_objs.
        role.permissions = [
            permission_objs[p] for p in perm_names if p in permission_objs
        ]

    db.session.commit()
