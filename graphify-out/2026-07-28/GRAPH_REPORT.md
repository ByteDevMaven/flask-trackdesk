# Graph Report - flask-trackdesk  (2026-07-28)

## Corpus Check
- 186 files · ~157,658 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1294 nodes · 2207 edges · 138 communities (115 shown, 23 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 129 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f595e47d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Core Models
- Inventory & Orders Service
- Invoices Service
- Accounting Module
- Community 5
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
- Community 98
- Community 99
- Community 100
- __init__.py
- str
- Community 105
- Community 106
- Community 108
- Community 109
- Account
- AccountType
- Community 113
- Community 114
- Community 115
- Community 116
- Centro de Mando Financiero
- journal_service.py
- _compute_account_balance
- Balanced Books Status
- Transaction
- stock_movement.py
- Warehouse Form
- .create_journal_entry
- send_low_stock_notifications
- document_sequence.py
- ActionRegistry
- .build_slug
- ExpenseStatus
- Flask

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 80 edges
2. `_is_ajax()` - 34 edges
3. `_sidebar_ctx()` - 20 edges
4. `resolve_company()` - 19 edges
5. `User` - 18 edges
6. `Document` - 17 edges
7. `CompanyService` - 16 edges
8. `InventoryService` - 16 edges
9. `UserService` - 15 edges
10. `ProjectService` - 14 edges

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
- 1-file cycle: `app/approvals/__init__.py -> app/approvals/__init__.py`
- 1-file cycle: `app/support/__init__.py -> app/support/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/pos/__init__.py -> app/pos/__init__.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 3-file cycle: `app/extensions.py -> app/models/user.py -> app/models/base.py -> app/extensions.py`
- 4-file cycle: `app/extensions.py -> app/models/user.py -> app/models/associations.py -> app/models/base.py -> app/extensions.py`

## Communities (138 total, 23 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.11
Nodes (38): add_invoice_payment(), _company_tax_rate(), delete_invoice_or_quote(), Soft delete an invoice or quote and its items., Add a payment to an invoice, post accounting income, and update its status., update_invoice_or_quote(), PosCashMovement, PosRegisterSession (+30 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.11
Nodes (31): print_invoice(), ClientCoords, _draw_client_info(), _draw_header(), _draw_items(), _draw_totals(), _generate_html_pdf(), generate_invoice_pdf() (+23 more)

### Community 3 - "Invoices Service"
Cohesion: 0.13
Nodes (17): _allowed_file(), _make_naive(), bool, int, str, Internal date / file helpers shared across accounting services., Strip timezone info so comparisons work with our stored naive datetimes., Save a single uploaded receipt; return relative URL or None.      Kept for legac (+9 more)

### Community 4 - "Accounting Module"
Cohesion: 0.12
Nodes (33): _active_expense_conditions(), _active_ledger_conditions(), _compute_account_balance(), _compute_balances_bulk(), _expenses_by_account(), _inventory_balance(), _is_receivable_account(), _ledger_manual_expenses_by_account() (+25 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (7): ProjectService, Return full P&L breakdown for a project., CompanyService, Find a company by its URL slug and check access permissions., Company, Project, Tag

### Community 7 - "PDF Generators"
Cohesion: 0.12
Nodes (28): addProduct(), calcTotals(), clearCart(), customerLabel(), escapeHtml(), filterClients(), filterProducts(), findExactProduct() (+20 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.06
Nodes (23): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+15 more)

### Community 9 - "Auth Module"
Cohesion: 0.20
Nodes (11): Notification, _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications(), recent(), send() (+3 more)

### Community 10 - "Users Service"
Cohesion: 0.20
Nodes (13): _create_balanced_transaction(), Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if ent, ExpenseService, Account, int, str, Expense CRUD service (create, read, update, delete)., Void old transaction and post a corrected balanced entry. (+5 more)

### Community 11 - "Barcode JS"
Cohesion: 0.06
Nodes (61): chart_of_accounts(), _company_url_id(), create_account(), create_expense(), create_income(), create_journal_entry(), create_loan(), create_project() (+53 more)

### Community 12 - "Payments Module"
Cohesion: 0.17
Nodes (8): create(), delete(), export(), update(), delete_purchase_order(), export_purchase_orders_xlsx(), Soft-delete a purchase order., Return (workbook, filename) tuple for all purchase orders matching criteria.

### Community 13 - "Companies Routes"
Cohesion: 0.32
Nodes (8): post_invoice_payment_income(), Account, int, Return the preferred revenue account for invoice-payment income., Post a balanced income transaction for an invoice payment.      The transactio, Return the preferred cash/bank asset account for a company., _resolve_cash_account(), _resolve_revenue_account()

### Community 14 - "Companies Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "NPM Config"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 16 - "Warehouses Service"
Cohesion: 0.20
Nodes (5): str, _match_context(), register_routes(), _result(), _search_tokens()

### Community 17 - "Invoice Form JS"
Cohesion: 0.50
Nodes (4): Project Create Edit Form, Nuevo Proyecto Page, Cost Center Profitability Management, Projects List Screen

### Community 18 - "Migrations Core"
Cohesion: 0.12
Nodes (12): ApprovalRequest, ApprovalStatus, ContactType, DocumentStatus, DocumentType, EmployeeClass, LeaveStatus, LeaveType (+4 more)

### Community 19 - "Drawer UI JS"
Cohesion: 0.29
Nodes (4): format_currency(), format_date(), Format a number as currency, Format a date in a readable format

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.38
Nodes (4): Flask, register_context_processors(), get_locale(), Config

### Community 21 - "Order Form JS"
Cohesion: 0.40
Nodes (4): AccountType, AccountService, Account, Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 22 - "Unify Contacts Migration"
Cohesion: 0.13
Nodes (9): Accounting integration helpers for invoice payments., Account, str, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa, float, str, Positive = debit effect, negative = credit effect. (+1 more)

### Community 23 - "Auto Migration"
Cohesion: 0.36
Nodes (6): Flask, register_blueprints(), Flask, register_request_hooks(), create_app(), init_action_handlers()

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
Cohesion: 0.40
Nodes (4): bool, str, Return True if this role carries *permission_name*., Role

### Community 29 - "Models Update Migration"
Cohesion: 0.06
Nodes (24): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password., bool, str (+16 more)

### Community 30 - "Audit Columns Migration"
Cohesion: 0.14
Nodes (6): JournalService, Record a new credit/loan.         Expects: memo, date, reference, amount, liabil, Record a payment towards a credit/loan.         Expects: memo, date, reference,, Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template., Returns a trial balance as of a given date.

### Community 31 - "Roles Migration"
Cohesion: 0.87
Nodes (5): _column_exists(), downgrade(), _index_exists(), _table_exists(), upgrade()

### Community 32 - "Warehouses Migration"
Cohesion: 0.11
Nodes (10): BaseModel, str, str, Project, str, str, str, str (+2 more)

### Community 33 - "Budget Migration"
Cohesion: 0.18
Nodes (5): Project CRUD, tagging, and reporting service., register_cli(), str, Report, Flask

### Community 34 - "Accounting Migration"
Cohesion: 0.67
Nodes (4): User Status Toggle Workflow, User Administration List Screen, User Danger Zone, User Profile Screen

### Community 35 - "Community 35"
Cohesion: 0.22
Nodes (9): Account CRUD and chart of accounts generation., Account, datetime, float, int, AccountingService — complete double-entry bookkeeping service.  This module re-e, Main AccountingService facade.     Inherits all @staticmethod methods from the d, DashboardService (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.23
Nodes (5): approve(), index(), reject(), api_adjust_stock(), ApprovalService

### Community 37 - "Community 37"
Cohesion: 0.19
Nodes (5): Contact, bool, str, Validate phone format (basic: digits, +, -, spaces)., Validate email format.

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
Cohesion: 0.14
Nodes (4): AlchemyEncoder, get_model_changes(), Helper to detect changed attributes and their values., str

### Community 43 - "Community 43"
Cohesion: 0.16
Nodes (12): Schedule Deviation Detail, Employee Editor Drawer, PTO Configuration, Employee Directory, Leave Request Form, Leave Request Queue, Leave Review Panel, Schedule Deviation Form (+4 more)

### Community 44 - "Community 44"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (21): Automated Tests, Database Models, Email Service Updates, Implementation Plan: Shared Company Email Threading, Manual Verification, [MODIFY] `app/models/enums.py`, [MODIFY] `app/models/__init__.py`, [MODIFY] `app/services/email_service.py` (+13 more)

### Community 46 - "Community 46"
Cohesion: 0.10
Nodes (17): Dashboard aggregation service., Company Model, Document, str, float, str, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached. (+9 more)

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
Cohesion: 0.67
Nodes (3): Stock Transfer Form, Product Detail Screen, Warehouse Stock Distribution

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
Cohesion: 0.29
Nodes (5): Company Routes, AuditMiddleware, Manually log a change. Useful if automated listeners are not enough., AuditLog, str

### Community 63 - "Community 63"
Cohesion: 0.08
Nodes (6): CategoryService, InventoryService, _item_ids_from_search_tag(), Fetch an item by its SKU within a company., Category, BaseModel

### Community 87 - "Community 87"
Cohesion: 0.31
Nodes (6): Return signed quantity change.         - incoming: always positive         - out, StockMovement, create_purchase_order(), _purchase_cost_from_form(), Use the submitted purchase cost, falling back to the item's cost price., update_purchase_order()

### Community 93 - "Community 93"
Cohesion: 0.33
Nodes (4): Expense, str, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor

### Community 95 - "Community 95"
Cohesion: 0.29
Nodes (3): InventoryItem, BaseModel, Auto-generate a SKU from the item name and its DB id.                  Example:

### Community 100 - "Community 100"
Cohesion: 0.24
Nodes (6): Employee, bool, float, str, Prefer the linked user's name when available., Deduct *days* from pto_balance if balance is sufficient. Returns True on success

### Community 103 - "__init__.py"
Cohesion: 0.48
Nodes (4): build_invoice_query(), export_invoice_report_xlsx(), get_invoice_list(), Return (workbook, filename) for all invoice rows matching the active filters.

### Community 104 - "str"
Cohesion: 0.09
Nodes (17): get_layout(), int, Retrieve the PdfTemplateLayout for the given company_id., AuditMiddleware.log_change, Registers global SQLAlchemy listeners for all models inheriting from Base., register_audit_listeners, init_error_handlers(), init_rbac() (+9 more)

### Community 109 - "Community 109"
Cohesion: 0.33
Nodes (6): Contact Form, Purchase Order Detail, Cross Module Search, Global Search, Warehouse List, Warehouse Stock Context

### Community 111 - "Account"
Cohesion: 0.53
Nodes (4): _create_expired_invoice_notification(), _invoice_link(), _notification_exists(), run_task()

### Community 117 - "Centro de Mando Financiero"
Cohesion: 0.67
Nodes (3): Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects

### Community 118 - "journal_service.py"
Cohesion: 0.33
Nodes (3): Journal entries, ledger, and trial balance service., AccountType, TransactionType

### Community 119 - "_compute_account_balance"
Cohesion: 0.19
Nodes (14): _get_period_bounds(), _parse_date(), Return (start_dt, end_dt) as naive datetimes for the given period., Parse YYYY-MM-DD string → naive datetime. Falls back to now(UTC)., IncomeService, Account, int, str (+6 more)

### Community 121 - "Transaction"
Cohesion: 0.18
Nodes (8): bool, float, str, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction, Transaction

### Community 123 - "stock_movement.py"
Cohesion: 0.50
Nodes (3): Project Financial Detail, Financial Reporting Workflow, Financial Reports

### Community 126 - ".create_journal_entry"
Cohesion: 0.33
Nodes (4): _parse_journal_lines(), Void old entry and post a corrected replacement., Parse and validate multi-line journal form data into entry dicts., Manual multi-line journal entry.         Expects form fields: memo, date, refere

### Community 127 - "send_low_stock_notifications"
Cohesion: 0.60
Nodes (5): _active_company_users(), _inventory_link(), _notification_exists(), send_low_stock_notifications(), run_task()

### Community 128 - "document_sequence.py"
Cohesion: 0.17
Nodes (24): audit_logs(), coerce_value(), dashboard(), database_browser(), database_delete_record(), database_edit_record(), database_fields(), database_new_record() (+16 more)

### Community 129 - "ActionRegistry"
Cohesion: 0.40
Nodes (3): ActionRegistry, Register a function to handle an approval action., Execute a registered action with the given payload.

### Community 131 - ".build_slug"
Cohesion: 0.29
Nodes (3): str, Auto-generate a URL-safe slug from the company name., upgrade()

## Knowledge Gaps
- **121 isolated node(s):** `User Review Required`, `Open Questions`, `[NEW] `app/models/communication.py``, `[MODIFY] `app/models/enums.py``, `[MODIFY] `app/models/__init__.py`` (+116 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseModel` connect `Warehouses Migration` to `Budget Migration`, `.build_slug`, `Community 100`, `Community 37`, `Auth Module`, `Detect Script`, `Community 43`, `Barcode JS`, `Community 46`, `Warehouses Service`, `Models Update Migration`, `Unify Contacts Migration`, `Transaction`, `Auto Migration 2`, `Community 60`, `Community 93`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `Document` connect `Community 46` to `Warehouses Migration`, `Budget Migration`, `Community 37`, `__init__.py`, `Account`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `CompanyService` connect `Community 5` to `Budget Migration`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `BaseModel` (e.g. with `Leave Request Form` and `AlchemyEncoder`) actually correct?**
  _`BaseModel` has 64 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Register a function to handle an approval action.`, `Execute a registered action with the given payload.`, `Format a number as currency` to the rest of the system?**
  _254 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Core Models` be split into smaller, more focused modules?**
  _Cohesion score 0.10852713178294573 - nodes in this community are weakly interconnected._
- **Should `Inventory & Orders Service` be split into smaller, more focused modules?**
  _Cohesion score 0.1073170731707317 - nodes in this community are weakly interconnected._