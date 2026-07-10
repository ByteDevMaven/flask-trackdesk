# Graph Report - flask-trackdesk  (2026-06-19)

## Corpus Check
- 171 files · ~136,375 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1220 nodes · 2656 edges · 115 communities (90 shown, 25 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 308 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `89d1a2c8`
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
- [[_COMMUNITY_Auto Migration 2|Auto Migration 2]]
- [[_COMMUNITY_Doc Templates Migration|Doc Templates Migration]]
- [[_COMMUNITY_Models Update Migration|Models Update Migration]]
- [[_COMMUNITY_Audit Columns Migration|Audit Columns Migration]]
- [[_COMMUNITY_Roles Migration|Roles Migration]]
- [[_COMMUNITY_Warehouses Migration|Warehouses Migration]]
- [[_COMMUNITY_Budget Migration|Budget Migration]]
- [[_COMMUNITY_Accounting Migration|Accounting Migration]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
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
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 102|Community 102]]
- [[_COMMUNITY_Community 103|Community 103]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]
- [[_COMMUNITY_Community 108|Community 108]]
- [[_COMMUNITY_Community 109|Community 109]]
- [[_COMMUNITY_Community 110|Community 110]]
- [[_COMMUNITY_Community 113|Community 113]]
- [[_COMMUNITY_Community 114|Community 114]]
- [[_COMMUNITY_Community 115|Community 115]]
- [[_COMMUNITY_Community 116|Community 116]]

## God Nodes (most connected - your core abstractions)
1. `resolve_company()` - 104 edges
2. `BaseModel` - 87 edges
3. `AccountType` - 45 edges
4. `ProjectService` - 43 edges
5. `datetime` - 39 edges
6. `TransactionType` - 35 edges
7. `Document` - 32 edges
8. `Company` - 27 edges
9. `_is_ajax()` - 22 edges
10. `str` - 22 edges

## Surprising Connections (you probably didn't know these)
- `run_task()` --calls--> `send_low_stock_notifications()`  [EXTRACTED]
  low_stock_notifications.py → app/inventory/services/low_stock_notifications.py
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `int` --uses--> `AccountType`  [INFERRED]
  app/accounting/services/dashboard_service.py → app/models/enums.py
- `create_leave()` --calls--> `Leave Request Form`  [EXTRACTED]
  app/hr/routes.py → app/hr/templates/hr/leave_form.html
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/audit.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/accounting/services/_helpers.py -> app/accounting/services/_helpers.py`
- 1-file cycle: `app/pos/__init__.py -> app/pos/__init__.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`

## Hyperedges (group relationships)
- **Financial Reporting Flow** — routes_reports, services_projectservice_compute_report, services__balance_ledger_revenue_by_account, services__balance_expenses_by_account, services__balance_replace_receivable_asset_balance [EXTRACTED 1.00]
- **Notification Center Flow** — notification_notification, routes_notifications_recent, routes_notifications_popups, routes_notifications_mark_read, js_index_notification_center [EXTRACTED 1.00]
- **Company Profile Extensions** — company_company, services_companyservice_save_logo, services_companyservice_normalize_timezone, versions_9f8e7d6c5b4a_company_timezone_logo_migration [EXTRACTED 1.00]
- **Application Shell Navigation Pattern** — templates_base_application_shell, templates_base_company_context, partials_nav_inventory_navigation, companies_index_company_list, search_results_global_search [EXTRACTED 1.00]
- **Financial Accounting Reporting Flow** — accounting_journal_libro_diario, accounting_ledger_libro_mayor, accounting_reports_financial_reports, accounting_report_pdf_financial_report_pdf, accounting_reports_financial_reporting_workflow [INFERRED 0.85]
- **Procurement Inventory Stock Flow** — orders_form_purchase_order_form, orders_view_purchase_order_detail, inventory_index_inventory_list, inventory_movements_stock_movements, warehouses_index_warehouse_list, orders_form_catalog_selection_workflow [INFERRED 0.85]

## Communities (115 total, 25 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.13
Nodes (33): str, int, str, Contact, Document, DocumentSequence, InventoryItem, PosCashMovement (+25 more)

### Community 1 - "App Init & Middleware"
Cohesion: 0.11
Nodes (37): chart_of_accounts(), _company_url_id(), create_account(), create_expense(), create_income(), create_journal_entry(), create_project(), create_tag() (+29 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.10
Nodes (28): bool, float, str, int, str, str, Company, Auto-generate a URL-safe slug from the company name. (+20 more)

### Community 3 - "Invoices Service"
Cohesion: 0.10
Nodes (31): int, bool, int, str, int, bool, Expense, AccountingAttachment (+23 more)

### Community 4 - "Accounting Module"
Cohesion: 0.16
Nodes (34): Account, int, str, datetime, float, _active_ledger_conditions(), _compute_account_balance(), _compute_balances_bulk() (+26 more)

### Community 6 - "HR Module"
Cohesion: 0.15
Nodes (9): str, str, str, str, str, BaseModel, UserStatus, Project (+1 more)

### Community 7 - "PDF Generators"
Cohesion: 0.12
Nodes (28): addProduct(), calcTotals(), clearCart(), customerLabel(), escapeHtml(), filterClients(), filterProducts(), findExactProduct() (+20 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.10
Nodes (10): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+2 more)

### Community 9 - "Auth Module"
Cohesion: 0.20
Nodes (11): Notification, _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications(), recent(), send() (+3 more)

### Community 10 - "Users Service"
Cohesion: 0.20
Nodes (10): Company Dashboard, Contact Form, Product Form, Purchase Order Detail, Inventory Navigation, Cross Module Search, Global Search, Warehouse Form (+2 more)

### Community 11 - "Barcode JS"
Cohesion: 0.18
Nodes (13): int, create(), delete(), edit(), export(), index(), update(), view() (+5 more)

### Community 12 - "Payments Module"
Cohesion: 0.11
Nodes (27): Helper to resolve a company from a route parameter that could be an integer ID o, resolve_company(), schedule_events(), schedules(), view_deviation(), view_leave(), api_adjust_stock(), api_bulk_delete() (+19 more)

### Community 13 - "Companies Routes"
Cohesion: 0.31
Nodes (9): Financial Document Payment Flow, Payment Invoice Association, Payment Method Selector, Payment Form Screen, Payment List Screen, Invoice Audit Log Modal, Invoice Detail Screen, Invoice Inline Payment Capture Form (+1 more)

### Community 14 - "Companies Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "NPM Config"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 17 - "Invoice Form JS"
Cohesion: 0.18
Nodes (11): Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects, Nuevo Proyecto Page, Cost Center Profitability Management, Projects List Screen, Balanced Books Status, Balanza de Comprobacion Screen (+3 more)

### Community 18 - "Migrations Core"
Cohesion: 0.13
Nodes (15): Libro Diario, Transaction Void Delete Workflow, Libro Mayor, Project Financial Detail, Financial Reporting Workflow, Financial Reports, str, int (+7 more)

### Community 19 - "Drawer UI JS"
Cohesion: 0.11
Nodes (13): api_search(), create(), delete(), edit(), index(), view(), format_currency(), format_date() (+5 more)

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.38
Nodes (5): int, str, BaseModel, InventoryItem, Auto-generate a SKU from the item name and its DB id.                  Example:

### Community 21 - "Order Form JS"
Cohesion: 0.38
Nodes (6): AccountType, Account, int, str, AccountService, Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 22 - "Unify Contacts Migration"
Cohesion: 0.15
Nodes (28): bool, str, bool, float, str, _allowed_file(), create_employee(), create_leave() (+20 more)

### Community 23 - "Auto Migration"
Cohesion: 0.33
Nodes (3): float, str, Total hours for this schedule entry.

### Community 24 - "Initial Migration"
Cohesion: 0.40
Nodes (4): str, Expense, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor

### Community 25 - "Schedule Migration"
Cohesion: 0.15
Nodes (17): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), closeProjectSearch(), filterInventoryProducts(), findExactInventoryProduct(), normalizeProductSearch(), openCustomerSearch() (+9 more)

### Community 26 - "Audit Migration"
Cohesion: 0.12
Nodes (15): dependencies, tailwindcss, devDependencies, concurrently, scripts, build, dev, i18n:all (+7 more)

### Community 27 - "Auto Migration 2"
Cohesion: 0.40
Nodes (4): bool, str, Return True if this role carries *permission_name*., Role

### Community 29 - "Models Update Migration"
Cohesion: 0.09
Nodes (8): bool, str, int, Contact, Validate phone format (basic: digits, +, -, spaces)., Validate email format., Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 30 - "Audit Columns Migration"
Cohesion: 0.40
Nodes (4): str, Account, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa

### Community 31 - "Roles Migration"
Cohesion: 0.87
Nodes (5): _column_exists(), downgrade(), _index_exists(), _table_exists(), upgrade()

### Community 32 - "Warehouses Migration"
Cohesion: 0.14
Nodes (21): int, str, Transaction, str, Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction, _create_balanced_transaction(), Double-entry Balance Rules (+13 more)

### Community 33 - "Budget Migration"
Cohesion: 0.07
Nodes (14): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password., EmailService, Sends a password reset email. (+6 more)

### Community 34 - "Accounting Migration"
Cohesion: 0.67
Nodes (4): User Status Toggle Workflow, User Administration List Screen, User Danger Zone, User Profile Screen

### Community 35 - "Community 35"
Cohesion: 0.14
Nodes (19): Account, datetime, float, int, int, float, int, DashboardService (+11 more)

### Community 36 - "Community 36"
Cohesion: 0.13
Nodes (25): int, str, Account, str, Account, str, Transaction, Account (+17 more)

### Community 37 - "Community 37"
Cohesion: 0.20
Nodes (4): str, InventoryService, _item_ids_from_search_tag(), Fetch an item by its SKU within a company.

### Community 38 - "Community 38"
Cohesion: 0.67
Nodes (5): _backfill_invoice_payment_revenue(), _column_exists(), downgrade(), _has_index(), upgrade()

### Community 39 - "Flash UI JS"
Cohesion: 0.29
Nodes (6): endpoint(), loadNotifications(), loadPopupNotifications(), notificationTypeClass(), notificationTypeLabel(), showNotificationPopup()

### Community 40 - "Index UI JS"
Cohesion: 0.32
Nodes (8): Contact Directory, Contact Type Filtering, Contact Detail Screen, Customer Invoice History, Supplier Product History, Dashboard Quick Actions, ERP Summary Dashboard, Company Scoped Navigation

### Community 41 - "Setup Script"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 42 - "Detect Script"
Cohesion: 0.06
Nodes (31): Flask, register_blueprints(), register_cli(), Flask, register_context_processors(), get_locale(), register_extensions(), Flask (+23 more)

### Community 43 - "Community 43"
Cohesion: 0.17
Nodes (13): int, str, Schedule Deviation Detail, Employee Editor Drawer, PTO Configuration, Employee Directory, Leave Request Form, Leave Request Queue (+5 more)

### Community 44 - "Community 44"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 45 - "Community 45"
Cohesion: 0.19
Nodes (7): bool, str, Return True if the user's role carries *permission_name*.         Superadmins (r, Shortcut — True when the user's role is 'superadmin' (platform admin)., True when the user's role is 'owner' (company-level admin)., User, UserMixin

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
Cohesion: 0.18
Nodes (8): str, AuditMiddleware, AlchemyEncoder, get_model_changes(), Manually log a change. Useful if automated listeners are not enough., Helper to detect changed attributes and their values., AuditLog, Company Routes

### Community 63 - "Community 63"
Cohesion: 0.67
Nodes (3): Python Application Dependencies, Flask Web Stack, PDF Excel Reporting Dependencies

### Community 95 - "Community 95"
Cohesion: 0.20
Nodes (8): create(), delete(), edit(), index(), search_invoices(), store(), update(), view()

### Community 96 - "Community 96"
Cohesion: 0.39
Nodes (6): export(), index(), build_invoice_query(), export_invoice_report_xlsx(), get_invoice_list(), Return (workbook, filename) for all invoice rows matching the active filters.

### Community 97 - "Community 97"
Cohesion: 0.33
Nodes (3): str, Lowercase file extension without leading dot (e.g. 'pdf', 'jpg')., Human-readable file size.

### Community 101 - "Community 101"
Cohesion: 0.08
Nodes (24): int, str, str, float, str, str, Company, _create_expired_invoice_notification() (+16 more)

### Community 102 - "Community 102"
Cohesion: 0.67
Nodes (3): Company Model, Global Search, Company Timezone and Logo Migration

### Community 109 - "Community 109"
Cohesion: 0.13
Nodes (19): str, create_invoice_or_quote, _generate_document_number, add_payment(), create(), delete(), edit(), print_invoice() (+11 more)

### Community 110 - "Community 110"
Cohesion: 0.29
Nodes (5): create(), edit(), index(), store(), update()

## Knowledge Gaps
- **111 isolated node(s):** `DocumentSequence`, `Contact`, `str`, `bool`, `bool` (+106 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `datetime` connect `Accounting Module` to `Core Models`, `App Init & Middleware`, `Warehouses Migration`, `Invoices Service`, `Community 35`, `Community 101`, `Community 5`, `Community 37`, `Inventory Routes`, `Auth Module`, `Detect Script`, `Community 96`, `Budget Migration`, `Community 109`, `Migrations Core`, `Community 60`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `HR Module` to `Inventory & Orders Service`, `Auth Module`, `Warehouses Service`, `Migrations Core`, `Consolidate Schema Migration`, `Unify Contacts Migration`, `Auto Migration`, `Initial Migration`, `Auto Migration 2`, `Models Update Migration`, `Audit Columns Migration`, `Warehouses Migration`, `Community 35`, `Community 36`, `Community 37`, `Community 43`, `Community 45`, `Community 60`, `Community 101`, `Community 103`, `Community 104`, `Community 109`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `resolve_company()` connect `Payments Module` to `Community 96`, `App Init & Middleware`, `Barcode JS`, `Community 109`, `Community 110`, `Drawer UI JS`, `Unify Contacts Migration`, `Community 95`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 70 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 70 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `AccountType` (e.g. with `int` and `str`) actually correct?**
  _`AccountType` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `ProjectService` (e.g. with `Account` and `datetime`) actually correct?**
  _`ProjectService` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Fetch an item by its SKU within a company.`, `Auto-generate a SKU from the item name and its DB id.                  Example:`, `DocumentSequence` to the rest of the system?**
  _230 weakly-connected nodes found - possible documentation gaps or missing edges._