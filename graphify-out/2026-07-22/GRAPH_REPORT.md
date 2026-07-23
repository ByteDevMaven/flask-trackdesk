# Graph Report - flask-trackdesk  (2026-07-22)

## Corpus Check
- 181 files · ~153,405 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1262 nodes · 2260 edges · 142 communities (104 shown, 38 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 147 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e19519a9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Core Models
- Inventory & Orders Service
- Invoices Service
- Accounting Module
- Community 5
- HR Module
- PDF Generators
- Inventory Routes
- Auth Module
- Users Service
- Barcode JS
- Payments Module
- Companies Routes
- Companies Service
- NPM Config
- Warehouses Service
- Invoice Form JS
- Migrations Core
- Drawer UI JS
- Consolidate Schema Migration
- Order Form JS
- Unify Contacts Migration
- Auto Migration
- Initial Migration
- Schedule Migration
- Audit Migration
- Auto Migration 2
- Doc Templates Migration
- Models Update Migration
- Audit Columns Migration
- Roles Migration
- Warehouses Migration
- Budget Migration
- Accounting Migration
- Community 35
- Community 36
- Community 37
- Community 38
- Flash UI JS
- Index UI JS
- Setup Script
- Detect Script
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 51
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 87
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 95
- post_invoice_payment_income
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- .create_journal_entry
- str
- Community 105
- Community 106
- Community 108
- Community 109
- DocumentStatus
- AccountType
- Community 113
- Community 114
- Community 115
- Community 116
- Centro de Mando Financiero
- warehouse.py
- LeaveType
- Balanced Books Status
- Transaction
- UserStatus
- Warehouse Form
- expire_documents.py
- send_low_stock_notifications
- .get_stock_movements
- purchase_order.py
- PaymentMethod
- PayPeriod
- .__repr__
- .__repr__
- str
- str
- str

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 80 edges
2. `ProjectService` - 39 edges
3. `_is_ajax()` - 34 edges
4. `Document` - 23 edges
5. `_sidebar_ctx()` - 20 edges
6. `_create_balanced_transaction()` - 19 edges
7. `resolve_company()` - 19 edges
8. `User` - 18 edges
9. `InventoryService` - 16 edges
10. `CompanyService` - 16 edges

## Surprising Connections (you probably didn't know these)
- `run_task()` --calls--> `send_low_stock_notifications()`  [EXTRACTED]
  low_stock_notifications.py → app/inventory/services/low_stock_notifications.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/payment.py → app/models/base.py
- `Company Timezone and Logo Migration` --implements--> `Company Model`  [EXTRACTED]
  migrations/versions/9f8e7d6c5b4a_add_company_timezone_and_logo.py → app/models/company.py
- `create_leave()` --calls--> `Leave Request Form`  [EXTRACTED]
  app/hr/routes.py → app/hr/templates/hr/leave_form.html
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/audit.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/accounting/services/_helpers.py -> app/accounting/services/_helpers.py`
- 1-file cycle: `app/support/__init__.py -> app/support/__init__.py`
- 1-file cycle: `app/pos/__init__.py -> app/pos/__init__.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 3-file cycle: `app/extensions.py -> app/models/user.py -> app/models/base.py -> app/extensions.py`
- 4-file cycle: `app/extensions.py -> app/models/user.py -> app/models/associations.py -> app/models/base.py -> app/extensions.py`

## Communities (142 total, 38 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.11
Nodes (38): add_invoice_payment(), _company_tax_rate(), delete_invoice_or_quote(), Soft delete an invoice or quote and its items., Add a payment to an invoice, post accounting income, and update its status., update_invoice_or_quote(), PosCashMovement, PosRegisterSession (+30 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.10
Nodes (31): print_invoice(), ClientCoords, _draw_client_info(), _draw_header(), _draw_items(), _draw_totals(), _generate_html_pdf(), generate_invoice_pdf() (+23 more)

### Community 3 - "Invoices Service"
Cohesion: 0.09
Nodes (30): _allowed_file(), _get_period_bounds(), _parse_date(), bool, int, str, Internal date / file helpers shared across accounting services., Return (start_dt, end_dt) as naive datetimes for the given period. (+22 more)

### Community 4 - "Accounting Module"
Cohesion: 0.16
Nodes (37): Account, _active_expense_conditions(), _active_ledger_conditions(), _compute_account_balance(), _compute_balances_bulk(), _expenses_by_account(), _is_receivable_account(), _ledger_manual_expenses_by_account() (+29 more)

### Community 6 - "HR Module"
Cohesion: 0.20
Nodes (11): api_delete_item(), api_update_item(), barcode(), delete(), drawer_adjust(), drawer_transfer(), edit(), transfer() (+3 more)

### Community 7 - "PDF Generators"
Cohesion: 0.12
Nodes (28): addProduct(), calcTotals(), clearCart(), customerLabel(), escapeHtml(), filterClients(), filterProducts(), findExactProduct() (+20 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.06
Nodes (23): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+15 more)

### Community 9 - "Auth Module"
Cohesion: 0.20
Nodes (11): Notification, _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications(), recent(), send() (+3 more)

### Community 11 - "Barcode JS"
Cohesion: 0.06
Nodes (57): chart_of_accounts(), _company_url_id(), create_account(), create_expense(), create_income(), create_journal_entry(), create_loan(), create_project() (+49 more)

### Community 12 - "Payments Module"
Cohesion: 0.15
Nodes (12): create(), delete(), export(), update(), create_purchase_order(), delete_purchase_order(), export_purchase_orders_xlsx(), _purchase_cost_from_form() (+4 more)

### Community 13 - "Companies Routes"
Cohesion: 0.17
Nodes (14): _create_balanced_transaction(), Double-entry Balance Rules, Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if ent, post_invoice_payment_income(), Account, int, Accounting integration helpers for invoice payments., Return the preferred revenue account for invoice-payment income. (+6 more)

### Community 14 - "Companies Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "NPM Config"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 16 - "Warehouses Service"
Cohesion: 0.24
Nodes (10): ExpenseService, Account, int, str, Expense CRUD service (create, read, update, delete)., Void old transaction and post a corrected balanced entry., Record an expense.          Double-entry:           DR  Expense Account    (amou, Return the first cash/bank account for the company, or raise ValueError. (+2 more)

### Community 17 - "Invoice Form JS"
Cohesion: 0.50
Nodes (4): Project Create Edit Form, Nuevo Proyecto Page, Cost Center Profitability Management, Projects List Screen

### Community 18 - "Migrations Core"
Cohesion: 0.11
Nodes (9): ContactType, DocumentStatus, DocumentType, EmployeeClass, ExpenseStatus, LeaveStatus, PTOAccrualPeriod, StockMovementType (+1 more)

### Community 19 - "Drawer UI JS"
Cohesion: 0.20
Nodes (8): register_blueprints(), format_currency(), format_date(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale, Flask

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.38
Nodes (3): _match_context(), _result(), _search_tokens()

### Community 21 - "Order Form JS"
Cohesion: 0.38
Nodes (6): AccountType, AccountService, Account, int, str, Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 23 - "Auto Migration"
Cohesion: 0.17
Nodes (8): api_bulk_delete(), api_get_items(), api_search(), api_stats(), export(), index(), InventoryService, _item_ids_from_search_tag()

### Community 24 - "Initial Migration"
Cohesion: 0.15
Nodes (11): create(), delete(), edit(), index(), search_invoices(), store(), update(), view() (+3 more)

### Community 25 - "Schedule Migration"
Cohesion: 0.15
Nodes (17): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), closeProjectSearch(), filterInventoryProducts(), findExactInventoryProduct(), normalizeProductSearch(), openCustomerSearch() (+9 more)

### Community 26 - "Audit Migration"
Cohesion: 0.12
Nodes (15): dependencies, tailwindcss, devDependencies, concurrently, scripts, build, dev, i18n:all (+7 more)

### Community 27 - "Auto Migration 2"
Cohesion: 0.33
Nodes (4): bool, str, Return True if this role carries *permission_name*., Role

### Community 29 - "Models Update Migration"
Cohesion: 0.05
Nodes (26): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password., _allowed_file(), bool (+18 more)

### Community 30 - "Audit Columns Migration"
Cohesion: 0.14
Nodes (6): JournalService, Record a new credit/loan.         Expects: memo, date, reference, amount, liabil, Record a payment towards a credit/loan.         Expects: memo, date, reference,, Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template., Returns a trial balance as of a given date.

### Community 31 - "Roles Migration"
Cohesion: 0.87
Nodes (5): _column_exists(), downgrade(), _index_exists(), _table_exists(), upgrade()

### Community 32 - "Warehouses Migration"
Cohesion: 0.11
Nodes (8): BaseModel, str, str, str, str, str, str, Transaction

### Community 33 - "Budget Migration"
Cohesion: 0.13
Nodes (13): Company Model, Document, str, float, str, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached., Calculate total amount paid via payments (+5 more)

### Community 34 - "Accounting Migration"
Cohesion: 0.67
Nodes (4): User Status Toggle Workflow, User Administration List Screen, User Danger Zone, User Profile Screen

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (19): Account CRUD and chart of accounts generation., Account, datetime, float, int, AccountingService — complete double-entry bookkeeping service.  This module re-e, Main AccountingService facade.     Inherits all @staticmethod methods from the d, DashboardService (+11 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (12): int, str, Project CRUD, tagging, and reporting service., Return full P&L breakdown for a project., Report, export_excel_response(), Generates an Excel file response., Company (+4 more)

### Community 37 - "Community 37"
Cohesion: 0.08
Nodes (14): build_invoice_query(), export_invoice_report_xlsx(), get_invoice_list(), Return (workbook, filename) for all invoice rows matching the active filters., Category, BaseModel, Contact, bool (+6 more)

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
Cohesion: 0.26
Nodes (10): register_cli(), Flask, register_context_processors(), get_locale(), register_extensions(), Flask, register_request_hooks(), create_app() (+2 more)

### Community 43 - "Community 43"
Cohesion: 0.16
Nodes (12): Schedule Deviation Detail, Employee Editor Drawer, PTO Configuration, Employee Directory, Leave Request Form, Leave Request Queue, Leave Review Panel, Schedule Deviation Form (+4 more)

### Community 44 - "Community 44"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (21): Automated Tests, Database Models, Email Service Updates, Implementation Plan: Shared Company Email Threading, Manual Verification, [MODIFY] `app/models/enums.py`, [MODIFY] `app/models/__init__.py`, [MODIFY] `app/services/email_service.py` (+13 more)

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
Nodes (8): Company Routes, AlchemyEncoder, AuditMiddleware, get_model_changes(), Manually log a change. Useful if automated listeners are not enough., Helper to detect changed attributes and their values., AuditLog, str

### Community 63 - "Community 63"
Cohesion: 0.14
Nodes (8): Project Financial Detail, Financial Reporting Workflow, Financial Reports, api_adjust_stock(), api_create_item(), create(), Return signed quantity change.         - incoming: always positive         - out, StockMovement

### Community 93 - "Community 93"
Cohesion: 0.40
Nodes (4): Expense, str, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor

### Community 96 - "post_invoice_payment_income"
Cohesion: 0.20
Nodes (5): categories(), create_category(), delete_category(), edit_category(), CategoryService

### Community 100 - "Community 100"
Cohesion: 0.24
Nodes (6): Employee, bool, float, str, Prefer the linked user's name when available., Deduct *days* from pto_balance if balance is sufficient. Returns True on success

### Community 101 - "Community 101"
Cohesion: 0.29
Nodes (3): str, Auto-generate a URL-safe slug from the company name., upgrade()

### Community 102 - "Community 102"
Cohesion: 0.33
Nodes (3): Journal entries, ledger, and trial balance service., AccountType, TransactionType

### Community 103 - ".create_journal_entry"
Cohesion: 0.33
Nodes (4): _parse_journal_lines(), Void old entry and post a corrected replacement., Parse and validate multi-line journal form data into entry dicts., Manual multi-line journal entry.         Expects form fields: memo, date, refere

### Community 104 - "str"
Cohesion: 0.28
Nodes (7): get_layout(), int, Retrieve the PdfTemplateLayout for the given company_id., AuditMiddleware.log_change, Registers global SQLAlchemy listeners for all models inheriting from Base., register_audit_listeners, init_error_handlers()

### Community 109 - "Community 109"
Cohesion: 0.33
Nodes (6): Contact Form, Purchase Order Detail, Cross Module Search, Global Search, Warehouse List, Warehouse Stock Context

### Community 111 - "DocumentStatus"
Cohesion: 0.43
Nodes (6): audit_logs(), dashboard(), deleted_items(), get_all_models(), record_view(), restore_item()

### Community 117 - "Centro de Mando Financiero"
Cohesion: 0.67
Nodes (3): Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects

### Community 118 - "warehouse.py"
Cohesion: 0.23
Nodes (5): edit(), index(), store(), update(), WarehouseService

### Community 123 - "UserStatus"
Cohesion: 0.33
Nodes (6): init_rbac(), Flask, RBAC Middleware =============== Plugged into the app via ``init_rbac(app)`` in `, Register the RBAC ``before_request`` hook on *app*., Seed the database with default roles and their permissions.      Roles     -----, seed_default_roles_and_permissions()

### Community 126 - "expire_documents.py"
Cohesion: 0.53
Nodes (4): _create_expired_invoice_notification(), _invoice_link(), _notification_exists(), run_task()

### Community 127 - "send_low_stock_notifications"
Cohesion: 0.60
Nodes (5): _active_company_users(), _inventory_link(), _notification_exists(), send_low_stock_notifications(), run_task()

## Knowledge Gaps
- **128 isolated node(s):** `User Review Required`, `Open Questions`, `[NEW] `app/models/communication.py``, `[MODIFY] `app/models/enums.py``, `[MODIFY] `app/models/__init__.py`` (+123 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `datetime` connect `Accounting Module` to `Core Models`, `Invoices Service`, `Community 5`, `Inventory Routes`, `Auth Module`, `Users Service`, `Barcode JS`, `Payments Module`, `Companies Routes`, `Warehouses Service`, `Auto Migration`, `Models Update Migration`, `Community 35`, `Community 36`, `Community 37`, `Detect Script`, `Community 60`, `Community 63`, `Community 102`, `expire_documents.py`, `send_low_stock_notifications`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `Warehouses Migration` to `purchase_order.py`, `.__repr__`, `.__repr__`, `str`, `str`, `Auth Module`, `Users Service`, `str`, `Barcode JS`, `Companies Routes`, `Unify Contacts Migration`, `Auto Migration 2`, `Models Update Migration`, `Budget Migration`, `Community 35`, `Community 36`, `Community 37`, `Community 43`, `Community 60`, `Community 93`, `Community 95`, `Community 100`, `Community 101`, `Transaction`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `Company Model` connect `Budget Migration` to `Warehouses Migration`, `Community 35`, `Community 5`, `Community 101`, `Users Service`, `Barcode JS`, `Models Update Migration`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `BaseModel` (e.g. with `Leave Request Form` and `AlchemyEncoder`) actually correct?**
  _`BaseModel` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `ProjectService` (e.g. with `accounting_service.py` and `Account`) actually correct?**
  _`ProjectService` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Format a number as currency`, `Format a date in a readable format`, `Format date according to the current locale` to the rest of the system?**
  _256 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Core Models` be split into smaller, more focused modules?**
  _Cohesion score 0.10852713178294573 - nodes in this community are weakly interconnected._