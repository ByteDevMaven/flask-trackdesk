# Graph Report - flask-trackdesk  (2026-06-16)

## Corpus Check
- 162 files · ~126,762 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1119 nodes · 2472 edges · 114 communities (94 shown, 20 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 322 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `366889f7`
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
- [[_COMMUNITY_Auto Migration 2|Auto Migration 2]]
- [[_COMMUNITY_Doc Templates Migration|Doc Templates Migration]]
- [[_COMMUNITY_Models Update Migration|Models Update Migration]]
- [[_COMMUNITY_Audit Columns Migration|Audit Columns Migration]]
- [[_COMMUNITY_Roles Migration|Roles Migration]]
- [[_COMMUNITY_Warehouses Migration|Warehouses Migration]]
- [[_COMMUNITY_Budget Migration|Budget Migration]]
- [[_COMMUNITY_Accounting Migration|Accounting Migration]]
- [[_COMMUNITY_HR Migration|HR Migration]]
- [[_COMMUNITY_Login Migration|Login Migration]]
- [[_COMMUNITY_Tags Migration|Tags Migration]]
- [[_COMMUNITY_Community 38|Community 38]]
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
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 102|Community 102]]
- [[_COMMUNITY_Community 103|Community 103]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]
- [[_COMMUNITY_Community 107|Community 107]]
- [[_COMMUNITY_Community 108|Community 108]]
- [[_COMMUNITY_Community 109|Community 109]]
- [[_COMMUNITY_Community 110|Community 110]]
- [[_COMMUNITY_Community 111|Community 111]]
- [[_COMMUNITY_Community 112|Community 112]]
- [[_COMMUNITY_Community 113|Community 113]]

## God Nodes (most connected - your core abstractions)
1. `resolve_company()` - 113 edges
2. `BaseModel` - 87 edges
3. `Flask` - 54 edges
4. `ProjectService` - 50 edges
5. `AccountType` - 46 edges
6. `TransactionType` - 36 edges
7. `Document` - 32 edges
8. `datetime` - 28 edges
9. `Company` - 27 edges
10. `ExpenseStatus` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `int` --uses--> `AccountType`  [INFERRED]
  app/accounting/services/dashboard_service.py → app/models/enums.py
- `float` --uses--> `ContactType`  [INFERRED]
  app/dashboard/services/dashboard_service.py → app/models/enums.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_item.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_template.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/accounting/services/_balance.py -> app/accounting/services/_balance.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/accounting/services/_helpers.py -> app/accounting/services/_helpers.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`

## Hyperedges (group relationships)
- **Financial Reporting Flow** — routes_reports, services_projectservice_compute_report, services__balance_ledger_revenue_by_account, services__balance_expenses_by_account, services__balance_replace_receivable_asset_balance [EXTRACTED 1.00]
- **Notification Center Flow** — notification_notification, routes_notifications_recent, routes_notifications_popups, routes_notifications_mark_read, js_index_notification_center [EXTRACTED 1.00]
- **Company Profile Extensions** — company_company, services_companyservice_save_logo, services_companyservice_normalize_timezone, versions_9f8e7d6c5b4a_company_timezone_logo_migration [EXTRACTED 1.00]
- **Application Shell Navigation Pattern** — templates_base_application_shell, templates_base_company_context, partials_nav_inventory_navigation, companies_index_company_list, search_results_global_search [EXTRACTED 1.00]
- **Financial Accounting Reporting Flow** — accounting_journal_libro_diario, accounting_ledger_libro_mayor, accounting_reports_financial_reports, accounting_report_pdf_financial_report_pdf, accounting_reports_financial_reporting_workflow [INFERRED 0.85]
- **Procurement Inventory Stock Flow** — orders_form_purchase_order_form, orders_view_purchase_order_detail, inventory_index_inventory_list, inventory_movements_stock_movements, warehouses_index_warehouse_list, orders_form_catalog_selection_workflow [INFERRED 0.85]

## Communities (114 total, 20 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.13
Nodes (14): bool, str, bool, str, Contact, Validate phone format (basic: digits, +, -, spaces)., ContactType, UserStatus (+6 more)

### Community 1 - "App Init & Middleware"
Cohesion: 0.14
Nodes (23): _company_url_id(), create_account(), create_journal_entry(), create_project(), create_tag(), delete_expense(), delete_income(), delete_journal_entry() (+15 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.10
Nodes (28): bool, float, str, int, str, str, Company, Auto-generate a URL-safe slug from the company name. (+20 more)

### Community 3 - "Invoices Service"
Cohesion: 0.18
Nodes (11): int, str, _parse_journal_lines(), Journal entries, ledger, and trial balance service., Parse and validate multi-line journal form data into entry dicts., Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template., Returns a trial balance as of a given date. (+3 more)

### Community 4 - "Accounting Module"
Cohesion: 0.07
Nodes (62): Account, Account, datetime, float, int, int, str, int (+54 more)

### Community 6 - "HR Module"
Cohesion: 0.12
Nodes (13): str, str, str, str, str, str, AuditLog, BaseModel (+5 more)

### Community 7 - "PDF Generators"
Cohesion: 0.27
Nodes (16): int, str, Account, Expense, int, str, bool, AccountType (+8 more)

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
Cohesion: 0.18
Nodes (13): int, create(), delete(), edit(), export(), index(), update(), view() (+5 more)

### Community 12 - "Payments Module"
Cohesion: 0.15
Nodes (23): Helper to resolve a company from a route parameter that could be an integer ID o, resolve_company(), api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_search() (+15 more)

### Community 13 - "Companies Routes"
Cohesion: 0.20
Nodes (14): Financial Document Payment Flow, Invoice Client Picker Modal, Invoice Or Quote Document Form Screen, Invoice Embedded Form Data, Invoice Product And Item Editor, Invoice Optional Project Picker, Payment Invoice Association, Payment Method Selector (+6 more)

### Community 14 - "Companies Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "NPM Config"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 17 - "Invoice Form JS"
Cohesion: 0.12
Nodes (19): Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects, Registrar Gasto Page, Nuevo Proyecto Page, Cost Center Profitability Management, Projects List Screen, Balanced Books Status (+11 more)

### Community 18 - "Migrations Core"
Cohesion: 0.15
Nodes (11): str, int, str, str, BaseModel, StockMovementType, Return signed quantity: negative for outgoing, positive for incoming/adjustment., create_purchase_order (+3 more)

### Community 19 - "Drawer UI JS"
Cohesion: 0.20
Nodes (7): format_currency(), format_date(), index(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.30
Nodes (8): delete_account(), AccountType, Account, int, str, AccountService, Account CRUD and chart of accounts generation., Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 21 - "Order Form JS"
Cohesion: 0.13
Nodes (20): str, str, create_invoice_or_quote, _generate_document_number, add_invoice_payment, update_invoice_or_quote, add_payment(), create() (+12 more)

### Community 22 - "Unify Contacts Migration"
Cohesion: 0.12
Nodes (20): str, int, str, int, str, str, Employee Editor Drawer, PTO Configuration (+12 more)

### Community 23 - "Auto Migration"
Cohesion: 0.14
Nodes (15): float, str, create_schedule(), delete_employee(), delete_leave(), delete_schedule(), edit_schedule(), employees() (+7 more)

### Community 25 - "Schedule Migration"
Cohesion: 0.18
Nodes (14): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), closeProjectSearch(), openCustomerSearch(), openProductSearch(), openProjectSearch(), renderCustomers() (+6 more)

### Community 26 - "Audit Migration"
Cohesion: 0.12
Nodes (15): dependencies, tailwindcss, devDependencies, concurrently, scripts, build, dev, i18n:all (+7 more)

### Community 27 - "Auto Migration 2"
Cohesion: 0.40
Nodes (4): bool, str, Return True if this role carries *permission_name*., Role

### Community 29 - "Models Update Migration"
Cohesion: 0.18
Nodes (3): int, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 30 - "Audit Columns Migration"
Cohesion: 0.40
Nodes (4): str, Account, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa

### Community 31 - "Roles Migration"
Cohesion: 0.29
Nodes (9): Account, int, str, Transaction, Income (revenue) CRUD service., Record an income / revenue event.          Double-entry:           DR  Cash /, Void old income transaction and create a corrected one., _resolve_cash_account() (+1 more)

### Community 33 - "Budget Migration"
Cohesion: 0.12
Nodes (5): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., Returns the companies of target_user that current_user is allowed to see., UserService, send_password_reset()

### Community 34 - "Accounting Migration"
Cohesion: 0.67
Nodes (4): User Status Toggle Workflow, User Administration List Screen, User Danger Zone, User Profile Screen

### Community 35 - "HR Migration"
Cohesion: 0.20
Nodes (7): bool, float, str, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction

### Community 36 - "Login Migration"
Cohesion: 0.33
Nodes (5): init_rbac(), RBAC Middleware =============== Plugged into the app via ``init_rbac(app)`` in `, Register the RBAC ``before_request`` hook on *app*., Seed the database with default roles and their permissions.      Roles     -----, seed_default_roles_and_permissions()

### Community 37 - "Tags Migration"
Cohesion: 0.15
Nodes (10): AuditMiddleware, AuditMiddleware.log_change, register_audit_listeners, AlchemyEncoder, get_model_changes(), Registers global SQLAlchemy listeners for all models inheriting from Base., Manually log a change. Useful if automated listeners are not enough., Helper to detect changed attributes and their values. (+2 more)

### Community 38 - "Community 38"
Cohesion: 0.67
Nodes (5): _backfill_invoice_payment_revenue(), _column_exists(), downgrade(), _has_index(), upgrade()

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
Cohesion: 0.13
Nodes (16): Account, int, float, str, Positive = debit effect, negative = credit effect., A single line in the accounting ledger.  Every entry MUST belong to a     Transa, post_invoice_payment_income(), Accounting integration helpers for invoice payments. (+8 more)

### Community 44 - "Community 44"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 45 - "Community 45"
Cohesion: 0.26
Nodes (12): bool, bool, float, str, create_employee(), edit_employee(), Employee, Prefer the linked user's name when available. (+4 more)

### Community 46 - "Community 46"
Cohesion: 0.18
Nodes (17): chart_of_accounts(), journal_list(), ledger(), _sidebar_ctx(), trial_balance(), export_excel_response(), Generates an Excel file response., create_income (+9 more)

### Community 47 - "Community 47"
Cohesion: 0.47
Nodes (3): attachDrawerFormSubmit(), loadDrawerContent(), openDrawer()

### Community 48 - "Community 48"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 49 - "Community 49"
Cohesion: 0.47
Nodes (3): _index_exists(), _table_exists(), upgrade()

### Community 53 - "Community 53"
Cohesion: 0.80
Nodes (4): _column_exists(), downgrade(), _has_index(), upgrade()

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

### Community 100 - "Community 100"
Cohesion: 0.21
Nodes (13): bool, datetime, str, Expense CRUD service (create, read, update, delete)., Record an expense.          Double-entry:           DR  Expense Account    (amou, _allowed_file(), _get_period_bounds(), _parse_date() (+5 more)

### Community 101 - "Community 101"
Cohesion: 0.17
Nodes (11): float, str, Document, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached., Calculate total amount paid via payments, Calculate remaining balance to be paid, Calculate total discount amount from document items. Cached. (+3 more)

### Community 102 - "Community 102"
Cohesion: 0.21
Nodes (6): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password.

### Community 104 - "Community 104"
Cohesion: 0.20
Nodes (8): create(), delete(), edit(), index(), search_invoices(), store(), update(), view()

### Community 108 - "Community 108"
Cohesion: 0.39
Nodes (3): EmailService, Sends a password reset email., Sends an error notification to the configured admin email.

### Community 109 - "Community 109"
Cohesion: 0.39
Nodes (6): export(), index(), build_invoice_query(), export_invoice_report_xlsx(), get_invoice_list(), Return (workbook, filename) for all invoice rows matching the active filters.

### Community 110 - "Community 110"
Cohesion: 0.29
Nodes (5): create(), edit(), index(), store(), update()

### Community 111 - "Community 111"
Cohesion: 0.60
Nodes (5): Schedule Deviation Detail, Leave Request Queue, Leave Review Panel, Schedule Deviation Form, Work Schedule Calendar

### Community 112 - "Community 112"
Cohesion: 0.67
Nodes (3): Libro Diario, Transaction Void Delete Workflow, Libro Mayor

### Community 113 - "Community 113"
Cohesion: 0.67
Nodes (3): Project Financial Detail, Financial Reporting Workflow, Financial Reports

## Knowledge Gaps
- **106 isolated node(s):** `Expense`, `Company`, `state`, `STATE_KEYS`, `history` (+101 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Flask` connect `Detect Script` to `App Init & Middleware`, `Inventory & Orders Service`, `Accounting Module`, `Community 5`, `Inventory Routes`, `Auth Module`, `Barcode JS`, `Payments Module`, `Warehouses Service`, `Migrations Core`, `Drawer UI JS`, `Order Form JS`, `Auto Migration`, `Models Update Migration`, `Budget Migration`, `Login Migration`, `Tags Migration`, `Community 44`, `Community 95`, `Community 96`, `Community 97`, `Community 100`, `Community 102`, `Community 104`, `Community 108`, `Community 109`, `Community 110`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `HR Module` to `Core Models`, `Warehouses Migration`, `Inventory & Orders Service`, `HR Migration`, `Accounting Module`, `Community 101`, `Tags Migration`, `Invoices Service`, `Auth Module`, `Community 43`, `Community 45`, `Migrations Core`, `Order Form JS`, `Unify Contacts Migration`, `Auto Migration`, `Auto Migration 2`, `Audit Columns Migration`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `resolve_company()` connect `Payments Module` to `Community 96`, `App Init & Middleware`, `Community 104`, `Barcode JS`, `Community 45`, `Community 46`, `Community 109`, `Community 110`, `Drawer UI JS`, `Consolidate Schema Migration`, `Order Form JS`, `Unify Contacts Migration`, `Auto Migration`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 70 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 70 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `ProjectService` (e.g. with `Account` and `datetime`) actually correct?**
  _`ProjectService` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `AccountType` (e.g. with `int` and `str`) actually correct?**
  _`AccountType` has 36 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Sends an error notification to the configured admin email.`, `Sends a password reset email.`, `Account CRUD and chart of accounts generation.` to the rest of the system?**
  _221 weakly-connected nodes found - possible documentation gaps or missing edges._