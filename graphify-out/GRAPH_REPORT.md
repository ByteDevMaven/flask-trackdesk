# Graph Report - flask-trackdesk  (2026-07-09)

## Corpus Check
- 175 files · ~139,613 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1204 nodes · 2336 edges · 124 communities (94 shown, 30 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bb325b36`
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
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 108
- Community 109
- Community 110
- Schedule Deviation Detail
- AccountType
- Community 113
- Community 114
- Community 115
- Community 116
- Centro de Mando Financiero
- .is_balanced
- .total_amount
- Balanced Books Status
- .__repr__
- str
- str

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 86 edges
2. `resolve_company()` - 81 edges
3. `ProjectService` - 40 edges
4. `_is_ajax()` - 33 edges
5. `Document` - 30 edges
6. `Company Model` - 28 edges
7. `_sidebar_ctx()` - 20 edges
8. `User` - 20 edges
9. `_create_balanced_transaction()` - 19 edges
10. `InventoryService` - 17 edges

## Surprising Connections (you probably didn't know these)
- `run_task()` --calls--> `send_low_stock_notifications()`  [EXTRACTED]
  low_stock_notifications.py → app/inventory/services/low_stock_notifications.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/payment.py → app/models/base.py
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `Company Timezone and Logo Migration` --implements--> `Company Model`  [EXTRACTED]
  migrations/versions/9f8e7d6c5b4a_add_company_timezone_and_logo.py → app/models/company.py
- `create_leave()` --calls--> `Leave Request Form`  [EXTRACTED]
  app/hr/routes.py → app/hr/templates/hr/leave_form.html

## Import Cycles
- 1-file cycle: `app/accounting/services/_helpers.py -> app/accounting/services/_helpers.py`
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/pos/__init__.py -> app/pos/__init__.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`

## Communities (124 total, 30 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.14
Nodes (32): PosCashMovement, PosRegisterSession, str, _available_stock(), _build_invoice_form(), cash_movement(), checkout(), close_register() (+24 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.10
Nodes (30): ClientCoords, _draw_client_info(), _draw_header(), _draw_items(), _draw_totals(), _generate_html_pdf(), generate_invoice_pdf(), _generate_overlay_pdf() (+22 more)

### Community 3 - "Invoices Service"
Cohesion: 0.09
Nodes (30): ExpenseService, Account, int, str, Expense CRUD service (create, read, update, delete)., Void old transaction and post a corrected balanced entry., Record an expense.          Double-entry:           DR  Expense Account    (amou, Return the first cash/bank account for the company, or raise ValueError. (+22 more)

### Community 4 - "Accounting Module"
Cohesion: 0.15
Nodes (38): Account, _active_expense_conditions(), _active_ledger_conditions(), _compute_account_balance(), _compute_balances_bulk(), _expenses_by_account(), _is_receivable_account(), _ledger_manual_expenses_by_account() (+30 more)

### Community 6 - "HR Module"
Cohesion: 0.17
Nodes (7): BaseModel, str, Project, str, str, Tag, Transaction

### Community 7 - "PDF Generators"
Cohesion: 0.12
Nodes (28): addProduct(), calcTotals(), clearCart(), customerLabel(), escapeHtml(), filterClients(), filterProducts(), findExactProduct() (+20 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.10
Nodes (13): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+5 more)

### Community 9 - "Auth Module"
Cohesion: 0.20
Nodes (11): Notification, _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications(), recent(), send() (+3 more)

### Community 10 - "Users Service"
Cohesion: 0.20
Nodes (10): Company Dashboard, Contact Form, Product Form, Inventory Navigation, Purchase Order Detail, Cross Module Search, Global Search, Warehouse Form (+2 more)

### Community 11 - "Barcode JS"
Cohesion: 0.13
Nodes (16): create_income(), create_loan(), create_project(), create_tag(), delete_account(), delete_attachment(), delete_expense(), delete_income() (+8 more)

### Community 12 - "Payments Module"
Cohesion: 0.14
Nodes (23): api_search(), api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_stats(), api_update_item() (+15 more)

### Community 13 - "Companies Routes"
Cohesion: 0.31
Nodes (9): Invoice Audit Log Modal, Invoice Detail Screen, Invoice Inline Payment Capture Form, Payment Invoice Association, Payment Method Selector, Payment Form Screen, Payment List Screen, Payment Detail Screen (+1 more)

### Community 14 - "Companies Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "NPM Config"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 17 - "Invoice Form JS"
Cohesion: 0.50
Nodes (4): Project Create Edit Form, Nuevo Proyecto Page, Cost Center Profitability Management, Projects List Screen

### Community 18 - "Migrations Core"
Cohesion: 0.10
Nodes (13): Journal entries, ledger, and trial balance service., ContactType, DocumentStatus, DocumentType, EmployeeClass, LeaveStatus, LeaveType, PaymentMethod (+5 more)

### Community 19 - "Drawer UI JS"
Cohesion: 0.17
Nodes (9): format_currency(), format_date(), index(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale, export_excel_response() (+1 more)

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.42
Nodes (4): InventoryItem, int, str, Auto-generate a SKU from the item name and its DB id.                  Example:

### Community 21 - "Order Form JS"
Cohesion: 0.38
Nodes (6): AccountType, AccountService, Account, int, str, Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 22 - "Unify Contacts Migration"
Cohesion: 0.11
Nodes (21): _allowed_file(), create_employee(), create_leave(), create_schedule(), delete_employee(), delete_leave(), delete_schedule(), edit_employee() (+13 more)

### Community 23 - "Auto Migration"
Cohesion: 0.33
Nodes (3): float, str, Total hours for this schedule entry.

### Community 24 - "Initial Migration"
Cohesion: 0.18
Nodes (10): int, str, Project CRUD, tagging, and reporting service., Return full P&L breakdown for a project., str, Report, Company, Project (+2 more)

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
Cohesion: 0.07
Nodes (16): Contact, bool, str, Validate phone format (basic: digits, +, -, spaces)., bool, str, Return True if the user's role carries *permission_name*.         Superadmins (r, Shortcut — True when the user's role is 'superadmin' (platform admin). (+8 more)

### Community 30 - "Audit Columns Migration"
Cohesion: 0.11
Nodes (10): JournalService, _parse_journal_lines(), Void old entry and post a corrected replacement., Record a new credit/loan.         Expects: memo, date, reference, amount, liabil, Parse and validate multi-line journal form data into entry dicts., Record a payment towards a credit/loan.         Expects: memo, date, reference,, Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template. (+2 more)

### Community 31 - "Roles Migration"
Cohesion: 0.87
Nodes (5): _column_exists(), downgrade(), _index_exists(), _table_exists(), upgrade()

### Community 32 - "Warehouses Migration"
Cohesion: 0.18
Nodes (14): _create_balanced_transaction(), Double-entry Balance Rules, Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if ent, IncomeService, Account, int, str, Transaction (+6 more)

### Community 33 - "Budget Migration"
Cohesion: 0.10
Nodes (10): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password., EmailService, Sends a password reset email. (+2 more)

### Community 34 - "Accounting Migration"
Cohesion: 0.67
Nodes (4): User Status Toggle Workflow, User Administration List Screen, User Danger Zone, User Profile Screen

### Community 35 - "Community 35"
Cohesion: 0.09
Nodes (24): Account CRUD and chart of accounts generation., Account, datetime, float, int, AccountingService — complete double-entry bookkeeping service.  This module re-e, Main AccountingService facade.     Inherits all @staticmethod methods from the d, DashboardService (+16 more)

### Community 36 - "Community 36"
Cohesion: 0.28
Nodes (8): post_invoice_payment_income(), Account, int, Return the preferred revenue account for invoice-payment income., Post a balanced income transaction for an invoice payment.      The transactio, Return the preferred cash/bank asset account for a company., _resolve_cash_account(), _resolve_revenue_account()

### Community 37 - "Community 37"
Cohesion: 0.07
Nodes (29): Libro Diario, Transaction Void Delete Workflow, Libro Mayor, Project Financial Detail, Financial Reporting Workflow, Financial Reports, InventoryService, _item_ids_from_search_tag() (+21 more)

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
Cohesion: 0.07
Nodes (35): Flask, register_blueprints(), register_cli(), Flask, register_context_processors(), get_locale(), register_extensions(), Flask (+27 more)

### Community 43 - "Community 43"
Cohesion: 0.22
Nodes (7): Employee Editor Drawer, PTO Configuration, Employee Directory, Leave Request Form, int, str, Calendar days of the leave (inclusive).

### Community 44 - "Community 44"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 45 - "Community 45"
Cohesion: 0.18
Nodes (14): chart_of_accounts(), _company_url_id(), create_journal_entry(), edit_journal_entry(), income_list(), journal_list(), ledger(), loans_list() (+6 more)

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
Cohesion: 0.67
Nodes (3): Python Application Dependencies, Flask Web Stack, PDF Excel Reporting Dependencies

### Community 93 - "Community 93"
Cohesion: 0.20
Nodes (3): int, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 95 - "Community 95"
Cohesion: 0.22
Nodes (7): create(), delete(), edit(), index(), search_invoices(), store(), update()

### Community 96 - "Community 96"
Cohesion: 0.24
Nodes (6): Employee, bool, float, str, Prefer the linked user's name when available., Deduct *days* from pto_balance if balance is sufficient. Returns True on success

### Community 97 - "Community 97"
Cohesion: 0.32
Nodes (6): add_invoice_payment(), _company_tax_rate(), Add a payment to an invoice, post accounting income, and update its status., update_invoice_or_quote(), Payment, str

### Community 101 - "Community 101"
Cohesion: 0.13
Nodes (11): Document, str, float, str, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached., Calculate total amount paid via payments, Calculate remaining balance to be paid (+3 more)

### Community 102 - "Community 102"
Cohesion: 0.29
Nodes (5): create(), delete(), edit(), index(), view()

### Community 104 - "Community 104"
Cohesion: 0.40
Nodes (4): create_expense(), edit_expense(), expenses_list(), ExpenseStatus

### Community 109 - "Community 109"
Cohesion: 0.14
Nodes (16): add_payment(), create(), delete(), edit(), index(), print_invoice(), store(), update() (+8 more)

### Community 110 - "Community 110"
Cohesion: 0.29
Nodes (5): create(), edit(), index(), store(), update()

### Community 111 - "Schedule Deviation Detail"
Cohesion: 0.60
Nodes (5): Schedule Deviation Detail, Leave Request Queue, Leave Review Panel, Schedule Deviation Form, Work Schedule Calendar

### Community 112 - "AccountType"
Cohesion: 0.50
Nodes (3): create_account(), edit_account(), AccountType

### Community 117 - "Centro de Mando Financiero"
Cohesion: 0.67
Nodes (3): Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects

## Knowledge Gaps
- **124 isolated node(s):** `DocumentType`, `DocumentStatus`, `StockMovementType`, `PaymentMethod`, `ContactType` (+119 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `datetime` connect `Accounting Module` to `Warehouses Migration`, `Community 97`, `Core Models`, `Community 35`, `Invoices Service`, `Community 5`, `Community 37`, `Community 101`, `Inventory Routes`, `Auth Module`, `Detect Script`, `Barcode JS`, `Community 109`, `Migrations Core`, `Initial Migration`, `Community 60`, `Models Update Migration`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `HR Module` to `Inventory & Orders Service`, `Auth Module`, `Warehouses Service`, `Consolidate Schema Migration`, `Auto Migration`, `Initial Migration`, `Auto Migration 2`, `Models Update Migration`, `Community 35`, `Community 37`, `Community 43`, `Community 60`, `Community 96`, `Community 97`, `Community 100`, `Community 101`, `Community 103`, `.is_balanced`, `.total_amount`, `.__repr__`, `str`, `str`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `Company Model` connect `Inventory & Orders Service` to `Community 35`, `Community 101`, `Community 5`, `HR Module`, `Detect Script`, `Barcode JS`, `Payments Module`, `Models Update Migration`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 70 inferred relationships involving `BaseModel` (e.g. with `Leave Request Form` and `AlchemyEncoder`) actually correct?**
  _`BaseModel` has 70 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ProjectService` (e.g. with `accounting_service.py` and `Account`) actually correct?**
  _`ProjectService` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `URL segment for company-scoped routes (slug preferred, else numeric id).`, `Journal entries, ledger, and trial balance service.`, `Parse and validate multi-line journal form data into entry dicts.` to the rest of the system?**
  _245 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Core Models` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._