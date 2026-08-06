# Graph Report - flask-trackdesk  (2026-08-05)

## Corpus Check
- 223 files · ~159,122 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1331 nodes · 2492 edges · 147 communities (122 shown, 25 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 134 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `31b66fbf`
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
- routes.py
- Community 43
- Community 44
- Community 45
- __init__.py
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
- account.py
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
- CategoryService
- journal_service.py
- _compute_account_balance
- Balanced Books Status
- Transaction
- category_service.py
- Warehouse Form
- .create_journal_entry
- send_low_stock_notifications
- document_sequence.py
- .hours_worked
- .build_slug
- ExpenseStatus
- api_adjust_stock
- Flask
- purchase_order_item.py
- Tag
- project.py
- ARCHITECTURE.md
- Account

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 76 edges
2. `_is_ajax()` - 30 edges
3. `_sidebar_ctx()` - 27 edges
4. `User` - 17 edges
5. `InventoryService` - 16 edges
6. `CompanyService` - 16 edges
7. `UserService` - 15 edges
8. `_is_ajax()` - 14 edges
9. `ProjectService` - 14 edges
10. `_company_url_id()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `run_task()` --calls--> `send_low_stock_notifications()`  [EXTRACTED]
  low_stock_notifications.py → app/inventory/services/low_stock_notifications.py
- `Company Timezone and Logo Migration` --implements--> `Company Model`  [EXTRACTED]
  migrations/versions/9f8e7d6c5b4a_add_company_timezone_and_logo.py → app/models/company.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/audit.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_item.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_sequence.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/accounting/views/__init__.py -> app/accounting/views/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/hr/views/__init__.py -> app/hr/views/__init__.py`
- 1-file cycle: `app/inventory/views/__init__.py -> app/inventory/views/__init__.py`
- 1-file cycle: `app/invoices/views/__init__.py -> app/invoices/views/__init__.py`
- 1-file cycle: `app/support/__init__.py -> app/support/__init__.py`
- 1-file cycle: `app/support/views/__init__.py -> app/support/views/__init__.py`
- 1-file cycle: `app/support/views/audit.py -> app/support/views/audit.py`
- 1-file cycle: `app/approvals/__init__.py -> app/approvals/__init__.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/pos/__init__.py -> app/pos/__init__.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 3-file cycle: `app/extensions.py -> app/models/user.py -> app/models/base.py -> app/extensions.py`
- 4-file cycle: `app/extensions.py -> app/models/user.py -> app/models/associations.py -> app/models/base.py -> app/extensions.py`

## Communities (147 total, 25 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.14
Nodes (36): create_invoice_or_quote(), add_invoice_payment(), Add a payment to an invoice, post accounting income, and update its status., add_payment(), str, cash_movement(), checkout(), close_register() (+28 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.09
Nodes (35): ClientCoords, _draw_client_info(), _draw_header(), _draw_items(), _draw_totals(), _generate_html_pdf(), generate_invoice_pdf(), generate_invoice_pdf_from_request() (+27 more)

### Community 3 - "Invoices Service"
Cohesion: 0.16
Nodes (18): _allowed_file(), _get_period_bounds(), _make_naive(), _parse_date(), bool, int, str, Internal date / file helpers shared across accounting services. (+10 more)

### Community 4 - "Accounting Module"
Cohesion: 0.11
Nodes (7): Compatibility loader for invoice route modules., _generate_document_number(), Return the latest CAI number when its invoice is converted to a quote., _release_latest_invoice_number(), store(), update(), datetime

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (7): ProjectService, Return full P&L breakdown for a project., CompanyService, Find a company by its URL slug and check access permissions., Company, Project, Tag

### Community 6 - "HR Module"
Cohesion: 0.14
Nodes (27): chart_of_accounts(), create_account(), create_tag(), delete_account(), delete_tag(), edit_account(), ledger(), reports() (+19 more)

### Community 7 - "PDF Generators"
Cohesion: 0.12
Nodes (28): addProduct(), calcTotals(), clearCart(), customerLabel(), escapeHtml(), filterClients(), filterProducts(), findExactProduct() (+20 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.14
Nodes (10): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+2 more)

### Community 9 - "Auth Module"
Cohesion: 0.29
Nodes (10): _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications(), recent(), send(), _serialize() (+2 more)

### Community 10 - "Users Service"
Cohesion: 0.24
Nodes (10): ExpenseService, Account, int, str, Expense CRUD service (create, read, update, delete)., Void old transaction and post a corrected balanced entry., Record an expense.          Double-entry:           DR  Expense Account    (amou, Return the first cash/bank account for the company, or raise ValueError. (+2 more)

### Community 11 - "Barcode JS"
Cohesion: 0.14
Nodes (14): Compatibility loader for HR route modules., _allowed_file(), _is_ajax(), _save_attachment(), create_employee(), delete_employee(), edit_employee(), create_leave() (+6 more)

### Community 12 - "Payments Module"
Cohesion: 0.12
Nodes (16): build_invoice_query(), export_invoice_report_xlsx(), get_invoice_list(), Return (workbook, filename) for all invoice rows matching the active filters., create(), delete(), export(), update() (+8 more)

### Community 13 - "Companies Routes"
Cohesion: 0.29
Nodes (9): post_invoice_payment_income(), Account, int, Accounting integration helpers for invoice payments., Return the preferred revenue account for invoice-payment income., Post a balanced income transaction for an invoice payment.      The transactio, Return the preferred cash/bank asset account for a company., _resolve_cash_account() (+1 more)

### Community 14 - "Companies Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "NPM Config"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 16 - "Warehouses Service"
Cohesion: 0.18
Nodes (4): Compatibility loader for inventory route modules., Helper to resolve a company from a route parameter that could be an integer ID o, resolve_company(), Flask

### Community 18 - "Migrations Core"
Cohesion: 0.12
Nodes (12): ApprovalRequest, ApprovalStatus, ContactType, DocumentStatus, DocumentType, EmployeeClass, LeaveStatus, LeaveType (+4 more)

### Community 19 - "Drawer UI JS"
Cohesion: 0.29
Nodes (4): format_currency(), format_date(), Format a number as currency, Format a date in a readable format

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.40
Nodes (3): Flask, register_context_processors(), Config

### Community 21 - "Order Form JS"
Cohesion: 0.40
Nodes (4): AccountType, AccountService, Account, Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 22 - "Unify Contacts Migration"
Cohesion: 0.29
Nodes (4): float, str, Positive = debit effect, negative = credit effect., A single line in the accounting ledger.  Every entry MUST belong to a     Transa

### Community 24 - "Initial Migration"
Cohesion: 0.19
Nodes (8): _company_invoice(), _parse_amount(), _parse_method(), _parse_payment_date(), PaymentService, datetime, _recalculate_invoice_status(), PaymentMethod

### Community 25 - "Schedule Migration"
Cohesion: 0.16
Nodes (18): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), closeProjectSearch(), filterInventoryProducts(), findExactInventoryProduct(), getProductSearchTerms(), normalizeProductSearch() (+10 more)

### Community 26 - "Audit Migration"
Cohesion: 0.12
Nodes (15): dependencies, tailwindcss, devDependencies, concurrently, scripts, build, dev, i18n:all (+7 more)

### Community 27 - "Auto Migration 2"
Cohesion: 0.20
Nodes (6): Compatibility loader for accounting route modules.  Routes are grouped by doma, bool, str, Return True if this role carries *permission_name*., Role, search()

### Community 29 - "Models Update Migration"
Cohesion: 0.25
Nodes (4): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., Returns the companies of target_user that current_user is allowed to see., UserService

### Community 30 - "Audit Columns Migration"
Cohesion: 0.14
Nodes (6): JournalService, Record a new credit/loan.         Expects: memo, date, reference, amount, liabil, Record a payment towards a credit/loan.         Expects: memo, date, reference,, Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template., Returns a trial balance as of a given date.

### Community 31 - "Roles Migration"
Cohesion: 0.87
Nodes (5): _column_exists(), downgrade(), _index_exists(), _table_exists(), upgrade()

### Community 32 - "Warehouses Migration"
Cohesion: 0.16
Nodes (9): BaseModel, str, Payment, str, Project, str, str, Report (+1 more)

### Community 33 - "Budget Migration"
Cohesion: 0.07
Nodes (50): _inventory_balance(), _is_receivable_account(), _open_invoice_receivable_balance(), _preferred_receivable_account(), Account, datetime, Return asset balances with AR replaced by open invoice balance., Return asset balances with Inventory replaced by calculated inventory value. (+42 more)

### Community 34 - "Accounting Migration"
Cohesion: 0.19
Nodes (5): Contact, bool, str, Validate phone format (basic: digits, +, -, spaces)., Validate email format.

### Community 35 - "Community 35"
Cohesion: 0.25
Nodes (9): Account CRUD and chart of accounts generation., Account, datetime, float, int, AccountingService — complete double-entry bookkeeping service.  This module re-e, Main AccountingService facade.     Inherits all @staticmethod methods from the d, DashboardService (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.16
Nodes (11): AuditMiddleware.log_change, Registers global SQLAlchemy listeners for all models inheriting from Base., register_audit_listeners, init_error_handlers(), init_rbac(), Flask, RBAC Middleware =============== Plugged into the app via ``init_rbac(app)`` in `, Register the RBAC ``before_request`` hook on *app*. (+3 more)

### Community 37 - "Community 37"
Cohesion: 0.33
Nodes (3): float, str, Total hours for this schedule entry.

### Community 38 - "Community 38"
Cohesion: 0.67
Nodes (5): _backfill_invoice_payment_revenue(), _column_exists(), downgrade(), _has_index(), upgrade()

### Community 39 - "Flash UI JS"
Cohesion: 0.35
Nodes (11): closePopupMenus(), endpoint(), loadNotifications(), loadPopupNotifications(), notificationTypeClass(), notificationTypeLabel(), postNotificationAction(), renderNotificationList() (+3 more)

### Community 40 - "Index UI JS"
Cohesion: 0.21
Nodes (6): Notification, PosCashMovement, PosRegisterSession, str, str, BaseModel

### Community 41 - "Setup Script"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 42 - "routes.py"
Cohesion: 0.33
Nodes (3): index(), reject(), ApprovalService

### Community 43 - "Community 43"
Cohesion: 0.22
Nodes (6): Employee Editor Drawer, PTO Configuration, Leave Request Form, int, str, Calendar days of the leave (inclusive).

### Community 44 - "Community 44"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (21): Automated Tests, Database Models, Email Service Updates, Implementation Plan: Shared Company Email Threading, Manual Verification, [MODIFY] `app/models/enums.py`, [MODIFY] `app/models/__init__.py`, [MODIFY] `app/services/email_service.py` (+13 more)

### Community 46 - "__init__.py"
Cohesion: 0.46
Nodes (4): Flask, register_blueprints(), create_app(), init_action_handlers()

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
Cohesion: 0.06
Nodes (29): CategoryService, InventoryService, _item_ids_from_search_tag(), Fetch an item by its SKU within a company., _validated_supplier_id(), api_adjust_stock(), api_bulk_delete(), api_create_item() (+21 more)

### Community 87 - "Community 87"
Cohesion: 0.19
Nodes (9): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password., export_excel_response(), Generates an Excel file response. (+1 more)

### Community 93 - "Community 93"
Cohesion: 0.19
Nodes (7): bool, str, Return True if the user's role carries *permission_name*.         Superadmins (r, Shortcut — True when the user's role is 'superadmin' (platform admin)., True when the user's role is 'owner' (company-level admin)., User, UserMixin

### Community 95 - "Community 95"
Cohesion: 0.15
Nodes (10): calculate_document_totals(), Document, _money(), Calculate invoice totals consistently using decimal, cent-rounded arithmetic., Return the net subtotal before tax using the current line items., Return tax calculated from the current subtotal and company rate., Calculate total amount paid via payments, Calculate remaining balance to be paid (+2 more)

### Community 96 - "post_invoice_payment_income"
Cohesion: 0.13
Nodes (27): AlchemyEncoder, get_model_changes(), Helper to detect changed attributes and their values., audit_logs(), coerce_value(), database_fields(), encode_primary_key(), field_value() (+19 more)

### Community 98 - "Community 98"
Cohesion: 0.21
Nodes (3): str, str, Transaction

### Community 100 - "Community 100"
Cohesion: 0.22
Nodes (6): Employee, bool, float, str, Prefer the linked user's name when available., Deduct *days* from pto_balance if balance is sufficient. Returns True on success

### Community 103 - "account.py"
Cohesion: 0.40
Nodes (4): Account, str, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa

### Community 104 - "str"
Cohesion: 0.23
Nodes (5): edit(), index(), store(), update(), WarehouseService

### Community 108 - "Community 108"
Cohesion: 0.36
Nodes (4): EmailService, Sends a password reset email., Sends an error notification to the configured admin email., send_password_reset()

### Community 109 - "Community 109"
Cohesion: 0.67
Nodes (3): Contact Form, Cross Module Search, Global Search

### Community 111 - "Account"
Cohesion: 0.53
Nodes (4): _create_expired_invoice_notification(), _invoice_link(), _notification_exists(), run_task()

### Community 112 - "AccountType"
Cohesion: 0.25
Nodes (5): Project Financial Detail, Financial Reporting Workflow, Financial Reports, Return signed quantity change.         - incoming: always positive         - out, StockMovement

### Community 115 - "Community 115"
Cohesion: 0.29
Nodes (3): InventoryItem, BaseModel, Auto-generate a SKU from the item name and its DB id.                  Example:

### Community 116 - "Community 116"
Cohesion: 0.29
Nodes (4): approve(), ActionRegistry, Register a function to handle an approval action., Execute a registered action with the given payload.

### Community 117 - "CategoryService"
Cohesion: 0.33
Nodes (5): create_project(), delete_project(), edit_project(), project_detail(), projects_list()

### Community 118 - "journal_service.py"
Cohesion: 0.33
Nodes (3): Journal entries, ledger, and trial balance service., AccountType, TransactionType

### Community 119 - "_compute_account_balance"
Cohesion: 0.23
Nodes (10): IncomeService, Account, int, str, Transaction, Income (revenue) CRUD service., Record an income / revenue event.          Double-entry:           DR  Cash /, Void an income transaction (soft delete). (+2 more)

### Community 121 - "Transaction"
Cohesion: 0.20
Nodes (7): bool, float, str, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction

### Community 123 - "category_service.py"
Cohesion: 0.33
Nodes (3): str, Lowercase file extension without leading dot (e.g. 'pdf', 'jpg')., Human-readable file size.

### Community 126 - ".create_journal_entry"
Cohesion: 0.33
Nodes (4): _parse_journal_lines(), Void old entry and post a corrected replacement., Parse and validate multi-line journal form data into entry dicts., Manual multi-line journal entry.         Expects form fields: memo, date, refere

### Community 127 - "send_low_stock_notifications"
Cohesion: 0.48
Nodes (6): register_cli(), _active_company_users(), _inventory_link(), _notification_exists(), send_low_stock_notifications(), run_task()

### Community 128 - "document_sequence.py"
Cohesion: 0.40
Nodes (4): Expense, str, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor

### Community 131 - ".build_slug"
Cohesion: 0.25
Nodes (5): Company Model, str, Auto-generate a URL-safe slug from the company name., upgrade(), Company Timezone and Logo Migration

### Community 134 - "Flask"
Cohesion: 0.67
Nodes (3): Schedule Deviation Detail, Leave Review Panel, Schedule Deviation Form

### Community 137 - "project.py"
Cohesion: 0.20
Nodes (6): Dashboard aggregation service., Project CRUD, tagging, and reporting service., create_income(), delete_income(), edit_income(), income_list()

## Knowledge Gaps
- **104 isolated node(s):** `Application structure`, `User Review Required`, `Open Questions`, `[NEW] `app/models/communication.py``, `[MODIFY] `app/models/enums.py`` (+99 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseModel` connect `Warehouses Migration` to `document_sequence.py`, `.hours_worked`, `Core Models`, `.build_slug`, `purchase_order_item.py`, `Tag`, `project.py`, `Warehouses Service`, `Unify Contacts Migration`, `Auto Migration 2`, `Budget Migration`, `Accounting Migration`, `Community 37`, `Index UI JS`, `Community 43`, `Community 60`, `Community 93`, `post_invoice_payment_income`, `Community 98`, `Community 100`, `account.py`, `Transaction`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `CompanyService` connect `Community 5` to `project.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `ProjectService` connect `Community 5` to `project.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 61 inferred relationships involving `BaseModel` (e.g. with `Leave Request Form` and `AlchemyEncoder`) actually correct?**
  _`BaseModel` has 61 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Application structure`, `Compatibility loader for accounting route modules.  Routes are grouped by doma`, `Public facade for accounting balance services.  Implementation is split by res` to the rest of the system?**
  _242 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Core Models` be split into smaller, more focused modules?**
  _Cohesion score 0.13658536585365855 - nodes in this community are weakly interconnected._
- **Should `Inventory & Orders Service` be split into smaller, more focused modules?**
  _Cohesion score 0.09292929292929293 - nodes in this community are weakly interconnected._