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
    'contacts.api_search': 'contacts.view',

    # ── Inventory ─────────────────────────────────────────────────────────
    'inventory.index':  'inventory.view',
    'inventory.view':   'inventory.view',
    'inventory.create': 'inventory.manage',
    'inventory.store':  'inventory.manage',
    'inventory.edit':   'inventory.manage',
    'inventory.update': 'inventory.manage',
    'inventory.delete': 'inventory.delete',
    'inventory.api_adjust_stock': 'inventory.manage',
    'inventory.api_bulk_delete':  'inventory.delete',
    'inventory.api_create_item':  'inventory.manage',
    'inventory.api_delete_item':  'inventory.delete',
    'inventory.api_get_item':     'inventory.view',
    'inventory.api_get_items':    'inventory.view',
    'inventory.api_search':       'inventory.view',
    'inventory.api_stats':        'inventory.view',
    'inventory.api_update_item':  'inventory.manage',
    'inventory.barcode':          'inventory.view',
    'inventory.drawer_adjust':    'inventory.manage',
    'inventory.drawer_transfer':  'inventory.manage',
    'inventory.export':           'inventory.view',
    'inventory.movements':        'inventory.view',
    'inventory.transfer':         'inventory.manage',

    # ── Warehouses (using inventory perms) ────────────────────────────────
    'warehouses.index':  'inventory.view',
    'warehouses.create': 'inventory.manage',
    'warehouses.store':  'inventory.manage',
    'warehouses.edit':   'inventory.manage',
    'warehouses.update': 'inventory.manage',

    # ── Orders ────────────────────────────────────────────────────────────
    'orders.index':  'orders.view',
    'orders.view':   'orders.view',
    'orders.create': 'orders.manage',
    'orders.store':  'orders.manage',
    'orders.edit':   'orders.manage',
    'orders.update': 'orders.manage',
    'orders.delete': 'orders.delete',
    'orders.export': 'orders.view',

    # ── Invoices ──────────────────────────────────────────────────────────
    'invoices.index':  'invoices.view',
    'invoices.view':   'invoices.view',
    'invoices.create': 'invoices.manage',
    'invoices.store':  'invoices.manage',
    'invoices.edit':   'invoices.manage',
    'invoices.update': 'invoices.manage',
    'invoices.delete': 'invoices.delete',
    'invoices.add_payment':   'invoices.manage',
    'invoices.item_row':      'invoices.manage',
    'invoices.print_invoice': 'invoices.view',

    # ── Payments ──────────────────────────────────────────────────────────
    'payments.index':  'payments.view',
    'payments.view':   'payments.view',
    'payments.create': 'payments.manage',
    'payments.store':  'payments.manage',
    'payments.edit':   'payments.manage',
    'payments.update': 'payments.manage',
    'payments.delete': 'payments.delete',
    'payments.search_invoices': 'payments.manage',

    # ── Companies ─────────────────────────────────────────────────────────
    'companies.index':  'companies.view',
    'companies.view':   'companies.view',
    'companies.create': 'companies.admin',
    'companies.store':  'companies.admin',
    'companies.edit':   'companies.manage',
    'companies.update': 'companies.manage',
    'companies.delete': 'companies.admin',
    'companies.search': 'companies.view',
    'companies.sequences_index':   'companies.manage',
    'companies.sequence_create':   'companies.manage',
    'companies.sequence_store':    'companies.manage',
    'companies.sequence_edit':     'companies.manage',
    'companies.sequence_update':   'companies.manage',
    'companies.sequence_delete':   'companies.manage',

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
    'accounting.reports':                   'accounting.view',
    'accounting.trial_balance':             'accounting.view',
    'accounting.journal_list':              'accounting.view',
    'accounting.expenses_list':             'accounting.view',
    'accounting.income_list':               'accounting.view',
    'accounting.projects_list':             'accounting.view',
    'accounting.project_detail':            'accounting.view',
    'accounting.create_expense':            'accounting.manage',
    'accounting.edit_expense':              'accounting.manage',
    'accounting.delete_expense':            'accounting.delete',
    'accounting.create_income':             'accounting.manage',
    'accounting.edit_income':               'accounting.manage',
    'accounting.delete_income':             'accounting.delete',
    'accounting.create_journal_entry':      'accounting.manage',
    'accounting.edit_journal_entry':        'accounting.manage',
    'accounting.void_transaction':          'accounting.manage',
    'accounting.create_project':            'accounting.manage',
    'accounting.edit_project':              'accounting.manage',
    'accounting.delete_project':            'accounting.delete',
    'accounting.create_account':            'accounting.manage',
    'accounting.edit_account':              'accounting.manage',
    'accounting.delete_account':            'accounting.delete',
    'accounting.generate_default_accounts': 'accounting.manage',
    'accounting.create_tag':                'accounting.manage',
    'accounting.delete_tag':                'accounting.manage',

    # ── HR ────────────────────────────────────────────────────────────────
    'hr.employees':                       'hr.view',
    'hr.create_employee':                 'hr.manage',
    'hr.edit_employee':                   'hr.manage',
    'hr.delete_employee':                 'hr.delete',
    'hr.leaves':                          'hr.view',
    'hr.create_leave':                    'hr.manage',
    'hr.edit_leave':                      'hr.manage',
    'hr.review_leave':                    'hr.manage',
    'hr.view_leave':                      'hr.view',
    'hr.schedules':                       'hr.view',
    'hr.schedule_events':                 'hr.view',
    'hr.create_schedule':                 'hr.manage',
    'hr.delete_schedule':                 'hr.delete',
    'hr.view_deviation':                  'hr.view',

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
        if not endpoint or endpoint in PUBLIC_ENDPOINTS or endpoint.endswith('.static'):
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
    superadmin – Platform-level admin (you / support team). Full access to everything,
                 all companies. The only role that bypasses has_permission checks.
    owner      – Company-level admin. Full control within their assigned company/companies.
                 Can manage users, sequences, accounting, etc. but cannot see other companies.
    manager    – Can create/edit most resources within their company. View-only accounting.
    accountant – Can manage invoices/payments/accounting. View-only everything else.
    viewer     – Read-only access to all resources in their company.
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

    # ── Role definitions ───────────────────────────────────────────────────
    role_definitions: dict[str, list[str]] = {
        # Platform admin — bypasses has_permission in code, but we still assign all
        # permissions so the seed is consistent and the role table is complete.
        'superadmin': list(all_permission_names),

        # Company owner — full control within their companies
        'owner': [
            'dashboard.view',
            'contacts.view',   'contacts.manage',   'contacts.delete',
            'inventory.view',  'inventory.manage',  'inventory.delete',
            'orders.view',     'orders.manage',     'orders.delete',
            'invoices.view',   'invoices.manage',   'invoices.delete',
            'payments.view',   'payments.manage',   'payments.delete',
            'companies.view',  'companies.manage',
            'companies.admin',                       # can delete their own company
            'users.view',      'users.manage',       # manage users within their company
            'accounting.view', 'accounting.manage',
            'hr.view',         'hr.manage',         'hr.delete',
        ],

        # General Manager — oversees operations, read-only on accounting.
        'manager': [
            'dashboard.view',
            'contacts.view',   'contacts.manage',   'contacts.delete',
            'inventory.view',  'inventory.manage',  'inventory.delete',
            'orders.view',     'orders.manage',
            'invoices.view',   'invoices.manage',
            'payments.view',   'payments.manage',   'payments.delete',
            'companies.view',
            'users.view',
            'accounting.view',
        ],

        # Accountant — financial operations and billing.
        'accountant': [
            'dashboard.view',
            'contacts.view',
            'inventory.view',
            'orders.view',
            'orders.view',     'orders.manage',     'orders.delete',
            'invoices.view',   'invoices.manage',   'invoices.delete',
            'payments.view',   'payments.manage',   'payments.delete',
            'companies.view',
            'users.view',
            'accounting.view', 'accounting.manage',
        ],

        # HR Manager — manages Human Resources and users, view-only basic company info.
        'hr_manager': [
            'dashboard.view',
            'companies.view',
            'users.view',      'users.manage',
            'hr.view',         'hr.manage',         'hr.delete',
        ],

        # Inventory Manager — controls inventory, warehouses, and purchasing orders.
        'inventory_manager': [
            'dashboard.view',
            'contacts.view',   'contacts.manage',
            'inventory.view',  'inventory.manage',  'inventory.delete',
            'orders.view',     'orders.manage',
            'invoices.view',   'invoices.manage',
            'payments.view',   'payments.manage',
            'companies.view',
        ],

        # Sales Manager — controls clients, orders, and billing.
        'sales_manager': [
            'dashboard.view',
            'contacts.view',   'contacts.manage',   'contacts.delete',
            'inventory.view',
            'orders.view',     'orders.manage',     'orders.delete',
            'invoices.view',   'invoices.manage',   'invoices.delete',
            'companies.view',
        ],

        # Staff — base employee operational access (view inventory, contacts, dashboard).
        'staff': [
            'dashboard.view',
            'contacts.view',
            'inventory.view',
        ],

        # Viewer — strictly read-only across operational modules (no HR, no accounting).
        'viewer': [
            'dashboard.view',
            'contacts.view',
            'inventory.view',
            'orders.view',
            'invoices.view',
            'companies.view',
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
