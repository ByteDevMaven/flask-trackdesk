# Graph Report - flask-trackdesk  (2026-06-15)

## Corpus Check
- 159 files · ~124,228 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1111 nodes · 2451 edges · 106 communities (89 shown, 17 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 327 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6799c549`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Core Models|Core Models]]
- [[_COMMUNITY_App Init & Middleware|App Init & Middleware]]
- [[_COMMUNITY_Inventory & Orders Service|Inventory & Orders Service]]
- [[_COMMUNITY_Invoices Service|Invoices Service]]
- [[_COMMUNITY_Accounting Module|Accounting Module]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_HR Module|HR Module]]
- [[_COMMUNITY_PDF Generators|PDF Generators]]
- [[_COMMUNITY_Inventory Routes|Inventory Routes]]
- [[_COMMUNITY_Auth Module|Auth Module]]
- [[_COMMUNITY_Users Service|Users Service]]
- [[_COMMUNITY_Barcode JS|Barcode JS]]
- [[_COMMUNITY_Payments Module|Payments Module]]
- [[_COMMUNITY_Companies Routes|Companies Routes]]
- [[_COMMUNITY_Companies Service|Companies Service]]
- [[_COMMUNITY_NPM Config|NPM Config]]
- [[_COMMUNITY_Warehouses Service|Warehouses Service]]
- [[_COMMUNITY_Invoice Form JS|Invoice Form JS]]
- [[_COMMUNITY_Migrations Core|Migrations Core]]
- [[_COMMUNITY_Drawer UI JS|Drawer UI JS]]
- [[_COMMUNITY_Consolidate Schema Migration|Consolidate Schema Migration]]
- [[_COMMUNITY_Order Form JS|Order Form JS]]
- [[_COMMUNITY_Unify Contacts Migration|Unify Contacts Migration]]
- [[_COMMUNITY_Auto Migration|Auto Migration]]
- [[_COMMUNITY_Initial Migration|Initial Migration]]
- [[_COMMUNITY_Schedule Migration|Schedule Migration]]
- [[_COMMUNITY_Audit Migration|Audit Migration]]
- [[_COMMUNITY_Doc Templates Migration|Doc Templates Migration]]
- [[_COMMUNITY_Models Update Migration|Models Update Migration]]
- [[_COMMUNITY_Audit Columns Migration|Audit Columns Migration]]
- [[_COMMUNITY_Roles Migration|Roles Migration]]
- [[_COMMUNITY_Warehouses Migration|Warehouses Migration]]
- [[_COMMUNITY_Budget Migration|Budget Migration]]
- [[_COMMUNITY_HR Migration|HR Migration]]
- [[_COMMUNITY_Login Migration|Login Migration]]
- [[_COMMUNITY_Tags Migration|Tags Migration]]
- [[_COMMUNITY_Modals UI JS|Modals UI JS]]
- [[_COMMUNITY_Flash UI JS|Flash UI JS]]
- [[_COMMUNITY_Index UI JS|Index UI JS]]
- [[_COMMUNITY_Setup Script|Setup Script]]
- [[_COMMUNITY_Detect Script|Detect Script]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 103|Community 103]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]
- [[_COMMUNITY_Community 107|Community 107]]

## God Nodes (most connected - your core abstractions)
1. `resolve_company()` - 113 edges
2. `BaseModel` - 87 edges
3. `Flask` - 53 edges
4. `ProjectService` - 50 edges
5. `AccountType` - 47 edges
6. `TransactionType` - 36 edges
7. `Document` - 33 edges
8. `CompanyService` - 31 edges
9. `Company` - 28 edges
10. `datetime` - 23 edges

## Surprising Connections (you probably didn't know these)
- `int` --uses--> `AccountType`  [INFERRED]
  app/accounting/services/dashboard_service.py → app/models/enums.py
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `float` --uses--> `ContactType`  [INFERRED]
  app/dashboard/services/dashboard_service.py → app/models/enums.py
- `create_leave()` --calls--> `Leave Request Form`  [EXTRACTED]
  app/hr/routes.py → app/hr/templates/hr/leave_form.html
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_item.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/accounting/services/_helpers.py -> app/accounting/services/_helpers.py`
- 1-file cycle: `app/accounting/services/_balance.py -> app/accounting/services/_balance.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 2-file cycle: `app/cli.py -> app/extensions.py -> app/cli.py`

## Hyperedges (group relationships)
- **Financial Reporting Flow** — routes_reports, services_projectservice_compute_report, services__balance_ledger_revenue_by_account, services__balance_expenses_by_account, services__balance_replace_receivable_asset_balance [EXTRACTED 1.00]
- **Notification Center Flow** — notification_notification, routes_notifications_recent, routes_notifications_popups, routes_notifications_mark_read, js_index_notification_center [EXTRACTED 1.00]
- **Company Profile Extensions** — company_company, services_companyservice_save_logo, services_companyservice_normalize_timezone, versions_9f8e7d6c5b4a_company_timezone_logo_migration [EXTRACTED 1.00]
- **Application Shell Navigation Pattern** — templates_base_application_shell, templates_base_company_context, partials_nav_inventory_navigation, companies_index_company_list, search_results_global_search [EXTRACTED 1.00]
- **Financial Accounting Reporting Flow** — accounting_journal_libro_diario, accounting_ledger_libro_mayor, accounting_reports_financial_reports, accounting_report_pdf_financial_report_pdf, accounting_reports_financial_reporting_workflow [INFERRED 0.85]
- **Procurement Inventory Stock Flow** — orders_form_purchase_order_form, orders_view_purchase_order_detail, inventory_index_inventory_list, inventory_movements_stock_movements, warehouses_index_warehouse_list, orders_form_catalog_selection_workflow [INFERRED 0.85]

## Communities (106 total, 17 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.25
Nodes (9): Account, int, post_invoice_payment_income(), Accounting integration helpers for invoice payments., Return the preferred revenue account for invoice-payment income., Post a balanced income transaction for an invoice payment.      The transactio, Return the preferred cash/bank asset account for a company., _resolve_cash_account() (+1 more)

### Community 1 - "App Init & Middleware"
Cohesion: 0.12
Nodes (36): chart_of_accounts(), _company_url_id(), create_account(), create_journal_entry(), create_project(), create_tag(), delete_expense(), delete_journal_entry() (+28 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.10
Nodes (28): bool, float, str, int, str, str, Company, Auto-generate a URL-safe slug from the company name. (+20 more)

### Community 3 - "Invoices Service"
Cohesion: 0.19
Nodes (10): int, str, _parse_journal_lines(), Journal entries, ledger, and trial balance service., Parse and validate multi-line journal form data into entry dicts., Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template., Returns a trial balance as of a given date. (+2 more)

### Community 4 - "Accounting Module"
Cohesion: 0.07
Nodes (60): Account, delete_project(), int, str, int, int, str, float (+52 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (15): str, Company.build_slug, Company Model, companies.store, companies.update, Global Search, Find a company by its URL slug and check access permissions., CompanyService (+7 more)

### Community 6 - "HR Module"
Cohesion: 0.12
Nodes (17): str, str, str, str, str, str, AuditLog, BaseModel (+9 more)

### Community 7 - "PDF Generators"
Cohesion: 0.19
Nodes (17): int, str, Account, Expense, int, str, ExpenseStatus, TransactionType (+9 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.10
Nodes (10): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+2 more)

### Community 9 - "Auth Module"
Cohesion: 0.20
Nodes (11): Notification, _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications(), recent(), send() (+3 more)

### Community 10 - "Users Service"
Cohesion: 0.18
Nodes (15): Company List, Company Dashboard, Contact Form, Product Form, Inventory List, Low Stock Threshold, Catalog Selection Workflow, Purchase Order Form (+7 more)

### Community 11 - "Barcode JS"
Cohesion: 0.16
Nodes (18): str, int, create(), delete(), edit(), export(), index(), update() (+10 more)

### Community 12 - "Payments Module"
Cohesion: 0.15
Nodes (23): Helper to resolve a company from a route parameter that could be an integer ID o, resolve_company(), api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_search() (+15 more)

### Community 13 - "Companies Routes"
Cohesion: 0.12
Nodes (24): Financial Document Payment Flow, Shared List Filter Pagination Pattern, Invoice Client Picker Modal, Invoice Or Quote Document Form Screen, Invoice Embedded Form Data, Invoice Product And Item Editor, Invoice Optional Project Picker, Payment Invoice Association (+16 more)

### Community 14 - "Companies Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "NPM Config"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 16 - "Warehouses Service"
Cohesion: 0.13
Nodes (11): Libro Diario, Transaction Void Delete Workflow, Libro Mayor, Project Financial Detail, Financial Reporting Workflow, Financial Reports, int, str (+3 more)

### Community 17 - "Invoice Form JS"
Cohesion: 0.10
Nodes (22): Account Type Groups, Plan de Cuentas Screen, Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects, Registrar Gasto Page, Nuevo Proyecto Page, Cost Center Profitability Management (+14 more)

### Community 18 - "Migrations Core"
Cohesion: 0.21
Nodes (6): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password.

### Community 19 - "Drawer UI JS"
Cohesion: 0.20
Nodes (7): format_currency(), format_date(), index(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.40
Nodes (4): str, Account, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa

### Community 21 - "Order Form JS"
Cohesion: 0.13
Nodes (21): create_invoice_or_quote, _generate_document_number, add_invoice_payment, update_invoice_or_quote, add_payment(), create(), delete(), edit() (+13 more)

### Community 22 - "Unify Contacts Migration"
Cohesion: 0.18
Nodes (17): bool, str, str, bool, float, str, str, _allowed_file() (+9 more)

### Community 23 - "Auto Migration"
Cohesion: 0.20
Nodes (3): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., Returns the companies of target_user that current_user is allowed to see.

### Community 24 - "Initial Migration"
Cohesion: 0.13
Nodes (18): float, str, create_leave(), create_schedule(), delete_employee(), delete_leave(), delete_schedule(), edit_leave() (+10 more)

### Community 25 - "Schedule Migration"
Cohesion: 0.18
Nodes (14): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), closeProjectSearch(), openCustomerSearch(), openProductSearch(), openProjectSearch(), renderCustomers() (+6 more)

### Community 26 - "Audit Migration"
Cohesion: 0.12
Nodes (15): dependencies, tailwindcss, devDependencies, concurrently, scripts, build, dev, i18n:all (+7 more)

### Community 29 - "Models Update Migration"
Cohesion: 0.20
Nodes (3): int, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 30 - "Audit Columns Migration"
Cohesion: 0.20
Nodes (11): Account, datetime, float, int, float, int, DashboardService, Account CRUD and chart of accounts generation. (+3 more)

### Community 31 - "Roles Migration"
Cohesion: 0.14
Nodes (23): delete_income(), bool, datetime, str, Account, int, str, Transaction (+15 more)

### Community 32 - "Warehouses Migration"
Cohesion: 0.23
Nodes (10): int, str, Employee Editor Drawer, PTO Configuration, Employee Directory, Leave Request Form, leaves(), LeaveStatus (+2 more)

### Community 33 - "Budget Migration"
Cohesion: 0.14
Nodes (13): bool, str, bool, str, Contact, Validate phone format (basic: digits, +, -, spaces)., ContactType, Return True if the user's role carries *permission_name*.         Superadmins (r (+5 more)

### Community 36 - "Login Migration"
Cohesion: 0.20
Nodes (8): create(), delete(), edit(), index(), search_invoices(), store(), update(), view()

### Community 37 - "Tags Migration"
Cohesion: 0.15
Nodes (10): AuditMiddleware, AuditMiddleware.log_change, register_audit_listeners, AlchemyEncoder, get_model_changes(), Registers global SQLAlchemy listeners for all models inheriting from Base., Manually log a change. Useful if automated listeners are not enough., Helper to detect changed attributes and their values. (+2 more)

### Community 39 - "Flash UI JS"
Cohesion: 0.31
Nodes (5): endpoint(), loadNotifications(), loadPopupNotifications(), notificationTypeClass(), showNotificationPopup()

### Community 40 - "Index UI JS"
Cohesion: 0.32
Nodes (8): Contact Directory, Contact Type Filtering, Contact Detail Screen, Customer Invoice History, Supplier Product History, Dashboard Quick Actions, ERP Summary Dashboard, Company Scoped Navigation

### Community 41 - "Setup Script"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 42 - "Detect Script"
Cohesion: 0.30
Nodes (11): register_cli(), Flask, register_context_processors(), get_locale(), register_extensions(), Flask, register_request_hooks(), create_app() (+3 more)

### Community 43 - "Community 43"
Cohesion: 0.43
Nodes (5): delete_account(), Account, int, AccountType, Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 44 - "Community 44"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 45 - "Community 45"
Cohesion: 0.32
Nodes (3): Sends an error notification to the configured admin email., Sends a password reset email., send_password_reset()

### Community 46 - "Community 46"
Cohesion: 0.29
Nodes (5): create(), edit(), index(), store(), update()

### Community 47 - "Community 47"
Cohesion: 0.47
Nodes (3): attachDrawerFormSubmit(), loadDrawerContent(), openDrawer()

### Community 48 - "Community 48"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 49 - "Community 49"
Cohesion: 0.47
Nodes (3): _index_exists(), _table_exists(), upgrade()

### Community 50 - "Community 50"
Cohesion: 0.40
Nodes (3): int, str, Auto-generate a SKU from the item name and its DB id.                  Example:

### Community 51 - "Community 51"
Cohesion: 0.60
Nodes (5): Schedule Deviation Detail, Leave Request Queue, Leave Review Panel, Schedule Deviation Form, Work Schedule Calendar

### Community 53 - "Community 53"
Cohesion: 0.80
Nodes (4): _column_exists(), downgrade(), _has_index(), upgrade()

### Community 54 - "Community 54"
Cohesion: 0.15
Nodes (9): str, float, str, BaseModel, Expense, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor, Positive = debit effect, negative = credit effect. (+1 more)

### Community 55 - "Community 55"
Cohesion: 0.50
Nodes (4): Stock Adjustment Form, Stock Transfer Form, Product Detail Screen, Warehouse Stock Distribution

### Community 56 - "Community 56"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 57 - "Community 57"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 58 - "Community 58"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 59 - "Community 59"
Cohesion: 0.83
Nodes (3): _column_exists(), downgrade(), upgrade()

### Community 60 - "Community 60"
Cohesion: 0.53
Nodes (4): _create_expired_invoice_notification(), _invoice_link(), _notification_exists(), run_task()

### Community 63 - "Community 63"
Cohesion: 0.67
Nodes (3): Python Application Dependencies, Flask Web Stack, PDF Excel Reporting Dependencies

### Community 95 - "Community 95"
Cohesion: 0.32
Nodes (3): _match_context(), _result(), _search_tokens()

### Community 96 - "Community 96"
Cohesion: 0.25
Nodes (6): api_search(), create(), delete(), edit(), index(), view()

### Community 97 - "Community 97"
Cohesion: 0.33
Nodes (6): Flask, init_rbac(), RBAC Middleware =============== Plugged into the app via ``init_rbac(app)`` in `, Register the RBAC ``before_request`` hook on *app*., Seed the database with default roles and their permissions.      Roles     -----, seed_default_roles_and_permissions()

### Community 98 - "Community 98"
Cohesion: 0.40
Nodes (3): bool, str, Return True if this role carries *permission_name*.

## Knowledge Gaps
- **107 isolated node(s):** `Expense`, `Company`, `state`, `STATE_KEYS`, `history` (+102 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Flask` connect `Detect Script` to `App Init & Middleware`, `Inventory & Orders Service`, `Accounting Module`, `Community 5`, `Inventory Routes`, `Auth Module`, `Barcode JS`, `Payments Module`, `Migrations Core`, `Drawer UI JS`, `Order Form JS`, `Auto Migration`, `Initial Migration`, `Auto Migration 2`, `Models Update Migration`, `Audit Columns Migration`, `Roles Migration`, `Accounting Migration`, `Login Migration`, `Tags Migration`, `Community 44`, `Community 45`, `Community 46`, `Community 95`, `Community 96`, `Community 97`, `Community 99`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `HR Module` to `Inventory & Orders Service`, `Accounting Module`, `Community 5`, `Auth Module`, `Barcode JS`, `Warehouses Service`, `Consolidate Schema Migration`, `Order Form JS`, `Unify Contacts Migration`, `Initial Migration`, `Warehouses Migration`, `Budget Migration`, `HR Migration`, `Tags Migration`, `Modals UI JS`, `Community 50`, `Community 54`, `Community 98`, `Community 100`, `Community 101`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `resolve_company()` connect `Payments Module` to `Community 96`, `App Init & Middleware`, `Warehouses Migration`, `Accounting Module`, `Login Migration`, `Community 43`, `Barcode JS`, `Community 46`, `Drawer UI JS`, `Order Form JS`, `Unify Contacts Migration`, `Initial Migration`, `Roles Migration`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 70 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 70 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `ProjectService` (e.g. with `Account` and `datetime`) actually correct?**
  _`ProjectService` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `AccountType` (e.g. with `int` and `str`) actually correct?**
  _`AccountType` has 37 INFERRED edges - model-reasoned connections that need verification._
- **What connects `RBAC Middleware =============== Plugged into the app via ``init_rbac(app)`` in ``, `Register the RBAC ``before_request`` hook on *app*.`, `Seed the database with default roles and their permissions.      Roles     -----` to the rest of the system?**
  _221 weakly-connected nodes found - possible documentation gaps or missing edges._