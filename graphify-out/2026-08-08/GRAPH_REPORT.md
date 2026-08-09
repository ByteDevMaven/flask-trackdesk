# Graph Report - flask-trackdesk  (2026-08-06)

## Corpus Check
- 223 files · ~159,975 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1328 nodes · 2504 edges · 137 communities (114 shown, 23 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 125 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eba75b2c`
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
- _parse_date
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
- Community 113
- Community 114
- expire_documents.py
- _compute_account_balance
- Transaction
- Warehouse Form
- Expense
- Tag
- .hours_worked
- .build_slug
- AlchemyEncoder
- get_model_changes
- Flask
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
- 1-file cycle: `app/invoices/views/__init__.py -> app/invoices/views/__init__.py`
- 1-file cycle: `app/support/__init__.py -> app/support/__init__.py`
- 1-file cycle: `app/inventory/views/__init__.py -> app/inventory/views/__init__.py`
- 1-file cycle: `app/accounting/views/__init__.py -> app/accounting/views/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/hr/views/__init__.py -> app/hr/views/__init__.py`
- 1-file cycle: `app/support/views/__init__.py -> app/support/views/__init__.py`
- 1-file cycle: `app/support/views/audit.py -> app/support/views/audit.py`
- 1-file cycle: `app/approvals/__init__.py -> app/approvals/__init__.py`
- 1-file cycle: `app/pos/__init__.py -> app/pos/__init__.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 3-file cycle: `app/extensions.py -> app/models/user.py -> app/models/base.py -> app/extensions.py`
- 4-file cycle: `app/extensions.py -> app/models/user.py -> app/models/associations.py -> app/models/base.py -> app/extensions.py`

## Communities (137 total, 23 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.16
Nodes (32): str, cash_movement(), checkout(), close_register(), index(), open_register(), _available_stock(), _build_invoice_form() (+24 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.11
Nodes (31): ClientCoords, _draw_client_info(), _draw_header(), _draw_items(), _draw_totals(), _generate_html_pdf(), generate_invoice_pdf(), generate_invoice_pdf_from_request() (+23 more)

### Community 3 - "Invoices Service"
Cohesion: 0.18
Nodes (9): int, Save multiple uploaded files and return a list of AccountingAttachment instances, _save_attachments(), AccountingAttachment, bool, str, Polymorphic attachment table shared by all accounting entry types.  reference_ty, Lowercase file extension without leading dot (e.g. 'pdf', 'jpg'). (+1 more)

### Community 4 - "Accounting Module"
Cohesion: 0.08
Nodes (21): Compatibility loader for invoice route modules., create_invoice_or_quote(), _generate_document_number(), Return the latest CAI number when its invoice is converted to a quote., Recalculate the active sequence's current value based on the maximum document, _release_latest_invoice_number(), sync_document_sequence(), add_invoice_payment() (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (7): ProjectService, Return full P&L breakdown for a project., CompanyService, Find a company by its URL slug and check access permissions., Company, Project, Tag

### Community 6 - "HR Module"
Cohesion: 0.11
Nodes (38): chart_of_accounts(), create_account(), create_tag(), delete_account(), delete_tag(), edit_account(), ledger(), reports() (+30 more)

### Community 7 - "PDF Generators"
Cohesion: 0.12
Nodes (28): addProduct(), calcTotals(), clearCart(), customerLabel(), escapeHtml(), filterClients(), filterProducts(), findExactProduct() (+20 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.11
Nodes (12): Compatibility loader for accounting route modules.  Routes are grouped by doma, List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit() (+4 more)

### Community 9 - "Auth Module"
Cohesion: 0.20
Nodes (11): Notification, _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications(), recent(), send() (+3 more)

### Community 10 - "Users Service"
Cohesion: 0.24
Nodes (10): ExpenseService, Account, int, str, Expense CRUD service (create, read, update, delete)., Void old transaction and post a corrected balanced entry., Record an expense.          Double-entry:           DR  Expense Account    (amou, Return the first cash/bank account for the company, or raise ValueError. (+2 more)

### Community 11 - "Barcode JS"
Cohesion: 0.14
Nodes (14): Compatibility loader for HR route modules., _allowed_file(), _is_ajax(), _save_attachment(), create_employee(), delete_employee(), edit_employee(), create_leave() (+6 more)

### Community 12 - "Payments Module"
Cohesion: 0.08
Nodes (16): Contact, bool, str, Validate phone format (basic: digits, +, -, spaces)., InventoryItem, BaseModel, Auto-generate a SKU from the item name and its DB id.                  Example:, Validate email format. (+8 more)

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
Cohesion: 0.29
Nodes (5): Company Routes, AuditMiddleware, Manually log a change. Useful if automated listeners are not enough., AuditLog, str

### Community 17 - "Invoice Form JS"
Cohesion: 0.22
Nodes (18): _inventory_balance(), _is_receivable_account(), _open_invoice_receivable_balance(), _preferred_receivable_account(), Account, datetime, Return asset balances with AR replaced by open invoice balance., Return asset balances with Inventory replaced by calculated inventory value. (+10 more)

### Community 18 - "Migrations Core"
Cohesion: 0.07
Nodes (14): ApprovalRequest, ApprovalStatus, ContactType, DocumentStatus, DocumentType, EmployeeClass, ExpenseStatus, LeaveStatus (+6 more)

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.29
Nodes (4): format_currency(), format_date(), Format a number as currency, Format a date in a readable format

### Community 21 - "Order Form JS"
Cohesion: 0.40
Nodes (4): AccountType, AccountService, Account, Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 22 - "Unify Contacts Migration"
Cohesion: 0.29
Nodes (4): float, str, Positive = debit effect, negative = credit effect., A single line in the accounting ledger.  Every entry MUST belong to a     Transa

### Community 23 - "Auto Migration"
Cohesion: 0.11
Nodes (3): register_cli(), barcode(), Flask

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
Cohesion: 0.40
Nodes (4): bool, str, Return True if this role carries *permission_name*., Role

### Community 29 - "Models Update Migration"
Cohesion: 0.25
Nodes (4): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., Returns the companies of target_user that current_user is allowed to see., UserService

### Community 30 - "Audit Columns Migration"
Cohesion: 0.12
Nodes (11): JournalService, _parse_journal_lines(), Void old entry and post a corrected replacement., Record a new credit/loan.         Expects: memo, date, reference, amount, liabil, Parse and validate multi-line journal form data into entry dicts., Record a payment towards a credit/loan.         Expects: memo, date, reference,, Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template. (+3 more)

### Community 31 - "Roles Migration"
Cohesion: 0.87
Nodes (5): _column_exists(), downgrade(), _index_exists(), _table_exists(), upgrade()

### Community 32 - "Warehouses Migration"
Cohesion: 0.14
Nodes (10): BaseModel, Payment, str, Project, str, str, str, str (+2 more)

### Community 33 - "Budget Migration"
Cohesion: 0.25
Nodes (17): _recent_active_expenses(), _active_expense_conditions(), _active_ledger_conditions(), Ledger rows count only when unlinked or tied to a non-voided transaction., Expense rows count only when unlinked or tied to a non-voided transaction., _expenses_by_account(), _ledger_manual_expenses_by_account(), _ledger_revenue_by_account() (+9 more)

### Community 34 - "Accounting Migration"
Cohesion: 0.18
Nodes (3): CategoryService, Category, BaseModel

### Community 35 - "Community 35"
Cohesion: 0.25
Nodes (9): Account, datetime, float, int, AccountingService — complete double-entry bookkeeping service.  This module re-e, Main AccountingService facade.     Inherits all @staticmethod methods from the d, DashboardService, Income (revenue) CRUD service. (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.16
Nodes (10): AuditMiddleware.log_change, Registers global SQLAlchemy listeners for all models inheriting from Base., register_audit_listeners, init_error_handlers(), init_rbac(), RBAC Middleware =============== Plugged into the app via ``init_rbac(app)`` in `, Register the RBAC ``before_request`` hook on *app*., Seed the database with default roles and their permissions.      Roles     ----- (+2 more)

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
Cohesion: 0.22
Nodes (6): PosCashMovement, PosRegisterSession, str, Return signed quantity change.         - incoming: always positive         - out, StockMovement, BaseModel

### Community 41 - "Setup Script"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 43 - "Community 43"
Cohesion: 0.22
Nodes (6): Employee Editor Drawer, PTO Configuration, Leave Request Form, int, str, Calendar days of the leave (inclusive).

### Community 44 - "Community 44"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (21): Automated Tests, Database Models, Email Service Updates, Implementation Plan: Shared Company Email Threading, Manual Verification, [MODIFY] `app/models/enums.py`, [MODIFY] `app/models/__init__.py`, [MODIFY] `app/services/email_service.py` (+13 more)

### Community 47 - "Community 47"
Cohesion: 0.67
Nodes (5): attachDrawerFormSubmit(), closeDrawer(), loadDrawerContent(), openDrawer(), reloadSection()

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

### Community 60 - "_parse_date"
Cohesion: 0.24
Nodes (12): _allowed_file(), _get_period_bounds(), _make_naive(), _parse_date(), bool, str, Internal date / file helpers shared across accounting services., Strip timezone info so comparisons work with our stored naive datetimes. (+4 more)

### Community 63 - "Community 63"
Cohesion: 0.08
Nodes (25): InventoryService, _item_ids_from_search_tag(), Fetch an item by its SKU within a company., _validated_supplier_id(), api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item() (+17 more)

### Community 87 - "Community 87"
Cohesion: 0.19
Nodes (9): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password., export_excel_response(), Generates an Excel file response. (+1 more)

### Community 93 - "Community 93"
Cohesion: 0.19
Nodes (7): bool, str, Return True if the user's role carries *permission_name*.         Superadmins (r, Shortcut — True when the user's role is 'superadmin' (platform admin)., True when the user's role is 'owner' (company-level admin)., User, UserMixin

### Community 95 - "Community 95"
Cohesion: 0.12
Nodes (14): build_invoice_query(), export_invoice_report_xlsx(), get_invoice_list(), Return (workbook, filename) for all invoice rows matching the active filters., calculate_document_totals(), Document, _money(), Calculate invoice totals consistently using decimal, cent-rounded arithmetic. (+6 more)

### Community 96 - "post_invoice_payment_income"
Cohesion: 0.22
Nodes (24): audit_logs(), coerce_value(), database_fields(), encode_primary_key(), field_value(), get_all_models(), get_database_table(), get_database_tables() (+16 more)

### Community 98 - "Community 98"
Cohesion: 0.18
Nodes (3): str, str, str

### Community 100 - "Community 100"
Cohesion: 0.22
Nodes (6): Employee, bool, float, str, Prefer the linked user's name when available., Deduct *days* from pto_balance if balance is sufficient. Returns True on success

### Community 103 - "account.py"
Cohesion: 0.40
Nodes (4): Account, str, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa

### Community 104 - "str"
Cohesion: 0.50
Nodes (4): _create_balanced_transaction(), datetime, Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if en, TransactionType

### Community 108 - "Community 108"
Cohesion: 0.36
Nodes (4): EmailService, Sends a password reset email., Sends an error notification to the configured admin email., send_password_reset()

### Community 109 - "Community 109"
Cohesion: 0.67
Nodes (3): Contact Form, Cross Module Search, Global Search

### Community 113 - "Community 113"
Cohesion: 0.05
Nodes (32): approve(), index(), reject(), Flask, register_blueprints(), Flask, register_context_processors(), Flask (+24 more)

### Community 114 - "Community 114"
Cohesion: 0.23
Nodes (5): edit(), index(), store(), update(), WarehouseService

### Community 119 - "_compute_account_balance"
Cohesion: 0.23
Nodes (9): IncomeService, Account, int, str, Transaction, Record an income / revenue event.          Double-entry:           DR  Cash /, Void an income transaction (soft delete)., Void old income transaction and create a corrected one. (+1 more)

### Community 121 - "Transaction"
Cohesion: 0.20
Nodes (7): bool, float, str, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction

### Community 126 - "Expense"
Cohesion: 0.40
Nodes (4): Expense, str, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor

### Community 131 - ".build_slug"
Cohesion: 0.25
Nodes (5): Company Model, str, Auto-generate a URL-safe slug from the company name., upgrade(), Company Timezone and Logo Migration

### Community 134 - "Flask"
Cohesion: 0.67
Nodes (3): Schedule Deviation Detail, Leave Review Panel, Schedule Deviation Form

### Community 137 - "project.py"
Cohesion: 0.18
Nodes (7): Account CRUD and chart of accounts generation., Dashboard aggregation service., Journal entries, ledger, and trial balance service., Project CRUD, tagging, and reporting service., AccountType, TransactionType, datetime

## Knowledge Gaps
- **97 isolated node(s):** `Application structure`, `User Review Required`, `Open Questions`, `[NEW] `app/models/communication.py``, `[MODIFY] `app/models/enums.py`` (+92 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseModel` connect `Warehouses Migration` to `Tag`, `.hours_worked`, `Core Models`, `.build_slug`, `AlchemyEncoder`, `HR Module`, `project.py`, `Auth Module`, `Payments Module`, `Warehouses Service`, `Unify Contacts Migration`, `Auto Migration 2`, `Audit Columns Migration`, `Community 37`, `Community 43`, `Community 93`, `post_invoice_payment_income`, `Community 98`, `Community 100`, `account.py`, `Transaction`, `Expense`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `Document` connect `Community 95` to `Index UI JS`, `project.py`, `Payments Module`, `Community 113`, `Auto Migration`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `User` connect `Community 93` to `Warehouses Migration`, `Community 98`, `Inventory Routes`, `Index UI JS`, `Payments Module`, `Community 87`, `Auto Migration`, `Models Update Migration`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 61 inferred relationships involving `BaseModel` (e.g. with `Leave Request Form` and `AlchemyEncoder`) actually correct?**
  _`BaseModel` has 61 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Return the latest CAI number when its invoice is converted to a quote.`, `Recalculate the active sequence's current value based on the maximum document`, `Soft delete an invoice or quote and its items.` to the rest of the system?**
  _237 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Inventory & Orders Service` be split into smaller, more focused modules?**
  _Cohesion score 0.1073170731707317 - nodes in this community are weakly interconnected._
- **Should `Accounting Module` be split into smaller, more focused modules?**
  _Cohesion score 0.07804878048780488 - nodes in this community are weakly interconnected._