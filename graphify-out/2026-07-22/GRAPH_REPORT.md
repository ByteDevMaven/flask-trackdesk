# Graph Report - flask-trackdesk  (2026-07-20)

## Corpus Check
- 180 files · ~153,179 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1242 nodes · 2303 edges · 126 communities (92 shown, 34 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 145 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ca30c545`
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
- get_layout
- UserStatus
- Warehouse Form

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 83 edges
2. `ProjectService` - 39 edges
3. `resolve_company()` - 37 edges
4. `_is_ajax()` - 34 edges
5. `Document` - 26 edges
6. `_sidebar_ctx()` - 20 edges
7. `_create_balanced_transaction()` - 19 edges
8. `User` - 19 edges
9. `InventoryService` - 17 edges
10. `CompanyService` - 16 edges

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
- 1-file cycle: `app/support/__init__.py -> app/support/__init__.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/pos/__init__.py -> app/pos/__init__.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/notifications/__init__.py -> app/notifications/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`

## Communities (126 total, 34 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.11
Nodes (38): add_invoice_payment(), _company_tax_rate(), delete_invoice_or_quote(), Soft delete an invoice or quote and its items., Add a payment to an invoice, post accounting income, and update its status., update_invoice_or_quote(), PosCashMovement, PosRegisterSession (+30 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.11
Nodes (30): ClientCoords, _draw_client_info(), _draw_header(), _draw_items(), _draw_totals(), _generate_html_pdf(), generate_invoice_pdf(), generate_invoice_pdf_from_request() (+22 more)

### Community 3 - "Invoices Service"
Cohesion: 0.10
Nodes (29): ExpenseService, Account, int, str, Expense CRUD service (create, read, update, delete)., Void old transaction and post a corrected balanced entry., Record an expense.          Double-entry:           DR  Expense Account    (amou, Return the first cash/bank account for the company, or raise ValueError. (+21 more)

### Community 4 - "Accounting Module"
Cohesion: 0.14
Nodes (41): Account, _active_expense_conditions(), _active_ledger_conditions(), _compute_account_balance(), _compute_balances_bulk(), _expenses_by_account(), _is_receivable_account(), _ledger_manual_expenses_by_account() (+33 more)

### Community 6 - "HR Module"
Cohesion: 0.05
Nodes (34): api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_items(), api_search(), api_stats(), api_update_item() (+26 more)

### Community 7 - "PDF Generators"
Cohesion: 0.12
Nodes (28): addProduct(), calcTotals(), clearCart(), customerLabel(), escapeHtml(), filterClients(), filterProducts(), findExactProduct() (+20 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.09
Nodes (20): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+12 more)

### Community 9 - "Auth Module"
Cohesion: 0.20
Nodes (11): Notification, _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications(), recent(), send() (+3 more)

### Community 10 - "Users Service"
Cohesion: 0.18
Nodes (8): Document, str, str, Refresh subtotal and tax caches, Payment, str, create_invoice_or_quote, _generate_document_number

### Community 11 - "Barcode JS"
Cohesion: 0.10
Nodes (36): chart_of_accounts(), _company_url_id(), create_account(), create_expense(), create_income(), create_journal_entry(), create_loan(), create_project() (+28 more)

### Community 12 - "Payments Module"
Cohesion: 0.14
Nodes (23): _allowed_file(), create_employee(), create_leave(), create_schedule(), delete_employee(), delete_leave(), delete_schedule(), edit_employee() (+15 more)

### Community 13 - "Companies Routes"
Cohesion: 0.13
Nodes (15): _create_balanced_transaction(), Double-entry Balance Rules, Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if ent, IncomeService, Account, int, str, Transaction (+7 more)

### Community 14 - "Companies Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "NPM Config"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 16 - "Warehouses Service"
Cohesion: 0.12
Nodes (4): Stream a live PDF preview using the most recent invoice for this company., Generate a PDF on the fly using the submitted form data for a live preview., templates_live_preview(), templates_preview()

### Community 17 - "Invoice Form JS"
Cohesion: 0.50
Nodes (4): Project Create Edit Form, Nuevo Proyecto Page, Cost Center Profitability Management, Projects List Screen

### Community 18 - "Migrations Core"
Cohesion: 0.12
Nodes (8): ContactType, DocumentType, EmployeeClass, ExpenseStatus, LeaveStatus, PaymentMethod, PayPeriod, StockMovementType

### Community 19 - "Drawer UI JS"
Cohesion: 0.20
Nodes (7): format_currency(), format_date(), index(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.15
Nodes (4): str, _match_context(), _result(), _search_tokens()

### Community 21 - "Order Form JS"
Cohesion: 0.33
Nodes (7): AccountType, AccountService, Account, int, str, Account CRUD and chart of accounts generation., Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 24 - "Initial Migration"
Cohesion: 0.20
Nodes (3): int, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

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
Nodes (23): bool, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password., str, bool (+15 more)

### Community 30 - "Audit Columns Migration"
Cohesion: 0.14
Nodes (6): JournalService, Record a new credit/loan.         Expects: memo, date, reference, amount, liabil, Record a payment towards a credit/loan.         Expects: memo, date, reference,, Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template., Returns a trial balance as of a given date.

### Community 31 - "Roles Migration"
Cohesion: 0.87
Nodes (5): _column_exists(), downgrade(), _index_exists(), _table_exists(), upgrade()

### Community 32 - "Warehouses Migration"
Cohesion: 0.12
Nodes (9): BaseModel, str, str, str, str, str, Tag, str (+1 more)

### Community 33 - "Budget Migration"
Cohesion: 0.20
Nodes (6): float, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached., Calculate total amount paid via payments, Calculate remaining balance to be paid, Calculate total discount amount from document items. Cached.

### Community 34 - "Accounting Migration"
Cohesion: 0.67
Nodes (4): User Status Toggle Workflow, User Administration List Screen, User Danger Zone, User Profile Screen

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (21): Account, datetime, float, int, AccountingService — complete double-entry bookkeeping service.  This module re-e, Main AccountingService facade.     Inherits all @staticmethod methods from the d, DashboardService, Dashboard aggregation service. (+13 more)

### Community 36 - "Community 36"
Cohesion: 0.19
Nodes (8): int, str, Report, export_excel_response(), Generates an Excel file response., object, Project, Tag

### Community 37 - "Community 37"
Cohesion: 0.06
Nodes (30): Project Financial Detail, Financial Reporting Workflow, Financial Reports, delete(), export(), build_invoice_query(), export_invoice_report_xlsx(), get_invoice_list() (+22 more)

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
Nodes (40): register_blueprints(), register_cli(), Flask, register_context_processors(), get_locale(), register_extensions(), Flask, register_request_hooks() (+32 more)

### Community 43 - "Community 43"
Cohesion: 0.15
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
Cohesion: 0.67
Nodes (3): Python Application Dependencies, Flask Web Stack, PDF Excel Reporting Dependencies

### Community 93 - "Community 93"
Cohesion: 0.40
Nodes (4): Expense, str, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor

### Community 96 - "post_invoice_payment_income"
Cohesion: 0.28
Nodes (8): post_invoice_payment_income(), Account, int, Return the preferred revenue account for invoice-payment income., Post a balanced income transaction for an invoice payment.      The transactio, Return the preferred cash/bank asset account for a company., _resolve_cash_account(), _resolve_revenue_account()

### Community 100 - "Community 100"
Cohesion: 0.22
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

### Community 109 - "Community 109"
Cohesion: 0.33
Nodes (6): Contact Form, Purchase Order Detail, Cross Module Search, Global Search, Warehouse List, Warehouse Stock Context

### Community 117 - "Centro de Mando Financiero"
Cohesion: 0.67
Nodes (3): Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects

## Knowledge Gaps
- **131 isolated node(s):** `User Review Required`, `Open Questions`, `[NEW] `app/models/communication.py``, `[MODIFY] `app/models/enums.py``, `[MODIFY] `app/models/__init__.py`` (+126 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `datetime` connect `Accounting Module` to `Core Models`, `Invoices Service`, `Community 5`, `Community 102`, `HR Module`, `Inventory Routes`, `Community 37`, `Users Service`, `Barcode JS`, `Auth Module`, `Companies Routes`, `Detect Script`, `Warehouses Service`, `Order Form JS`, `Community 60`, `Models Update Migration`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `Warehouses Migration` to `Auth Module`, `Users Service`, `Payments Module`, `Companies Routes`, `Consolidate Schema Migration`, `Unify Contacts Migration`, `Auto Migration`, `Auto Migration 2`, `Models Update Migration`, `Budget Migration`, `Community 35`, `Community 36`, `Community 37`, `Community 43`, `Community 60`, `Community 93`, `Community 95`, `Community 100`, `Community 101`, `warehouse.py`, `Transaction`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `ProjectService` connect `Accounting Module` to `Warehouses Migration`, `Invoices Service`, `Community 35`, `Community 36`, `str`, `Users Service`, `Companies Routes`, `Community 93`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 67 inferred relationships involving `BaseModel` (e.g. with `Leave Request Form` and `AlchemyEncoder`) actually correct?**
  _`BaseModel` has 67 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `ProjectService` (e.g. with `accounting_service.py` and `Account`) actually correct?**
  _`ProjectService` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Fetch an item by its SKU within a company.`, `Auto-generate a SKU from the item name and its DB id.                  Example:`, `Stream a live PDF preview using the most recent invoice for this company.` to the rest of the system?**
  _259 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Core Models` be split into smaller, more focused modules?**
  _Cohesion score 0.10852713178294573 - nodes in this community are weakly interconnected._