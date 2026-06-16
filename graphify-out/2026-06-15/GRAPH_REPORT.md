# Graph Report - .  (2026-06-15)

## Corpus Check
- 43 files · ~124,006 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1124 nodes · 2501 edges · 95 communities (83 shown, 12 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 332 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
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

## God Nodes (most connected - your core abstractions)
1. `resolve_company()` - 113 edges
2. `BaseModel` - 88 edges
3. `Flask` - 54 edges
4. `ProjectService` - 50 edges
5. `AccountType` - 47 edges
6. `TransactionType` - 36 edges
7. `Document` - 33 edges
8. `CompanyService` - 31 edges
9. `Company` - 28 edges
10. `ExpenseStatus` - 23 edges

## Surprising Connections (you probably didn't know these)
- `int` --uses--> `AccountType`  [INFERRED]
  app/accounting/services/dashboard_service.py → app/models/enums.py
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `create_leave()` --calls--> `Leave Request Form`  [EXTRACTED]
  app/hr/routes.py → app/hr/templates/hr/leave_form.html
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_item.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_sequence.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/accounting/services/_balance.py -> app/accounting/services/_balance.py`
- 1-file cycle: `app/routes.py -> app/routes.py`
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
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

## Communities (95 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (45): Flask, Flask, register_cli(), Flask, register_context_processors(), get_locale(), register_extensions(), Flask (+37 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (44): chart_of_accounts(), _company_url_id(), create_account(), create_journal_entry(), create_project(), create_tag(), delete_expense(), delete_income() (+36 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (30): bool, float, str, int, str, str, str, Company (+22 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (25): bool, datetime, str, int, str, bool, Record an expense.          Double-entry:           DR  Expense Account    (amou, _allowed_file() (+17 more)

### Community 4 - "Community 4"
Cohesion: 0.17
Nodes (33): Account, int, str, datetime, float, _active_expense_conditions(), _active_ledger_conditions(), _compute_account_balance() (+25 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (15): str, Company.build_slug, Company Model, companies.store, companies.update, Global Search, Find a company by its URL slug and check access permissions., CompanyService (+7 more)

### Community 6 - "Community 6"
Cohesion: 0.17
Nodes (10): str, str, str, AuditLog, BaseModel, UserStatus, Expense, Represents a business expense (outflow of money).      Income / revenue is recor (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (26): int, str, Account, Expense, int, str, Account, int (+18 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (17): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (20): str, Header Notification Center JS, Notification Delivery Workflow, _can_send_notifications(), index(), mark_all_read(), popups(), _query_current_user_notifications() (+12 more)

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (27): Libro Diario, Transaction Void Delete Workflow, Libro Mayor, Project Financial Detail, Financial Reporting Workflow, Financial Reports, Company Profile Form, Company List (+19 more)

### Community 11 - "Community 11"
Cohesion: 0.15
Nodes (19): str, BaseModel, int, create(), delete(), edit(), export(), index() (+11 more)

### Community 12 - "Community 12"
Cohesion: 0.16
Nodes (23): Helper to resolve a company from a route parameter that could be an integer ID o, resolve_company(), api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_search() (+15 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (24): Financial Document Payment Flow, Shared List Filter Pagination Pattern, Invoice Client Picker Modal, Invoice Or Quote Document Form Screen, Invoice Embedded Form Data, Invoice Product And Item Editor, Invoice Optional Project Picker, Payment Invoice Association (+16 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 15 - "Community 15"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 16 - "Community 16"
Cohesion: 0.17
Nodes (10): str, int, str, str, create_invoice_or_quote, update_invoice_or_quote, StockMovementType, Payment (+2 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (22): Account Type Groups, Plan de Cuentas Screen, Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects, Registrar Gasto Page, Nuevo Proyecto Page, Cost Center Profitability Management (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (8): bool, str, str, Authenticate a user by email and password.         Returns (user, error_message), Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password., str

### Community 19 - "Community 19"
Cohesion: 0.11
Nodes (14): api_search(), create(), delete(), edit(), index(), view(), format_currency(), format_date() (+6 more)

### Community 20 - "Community 20"
Cohesion: 0.16
Nodes (12): Account, datetime, float, int, str, Account, Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa, Tag (+4 more)

### Community 21 - "Community 21"
Cohesion: 0.11
Nodes (17): _generate_document_number, add_invoice_payment, add_payment(), create(), delete(), edit(), index(), print_invoice() (+9 more)

### Community 22 - "Community 22"
Cohesion: 0.25
Nodes (13): bool, str, bool, float, str, create_employee(), edit_employee(), Employee (+5 more)

### Community 23 - "Community 23"
Cohesion: 0.20
Nodes (3): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., Returns the companies of target_user that current_user is allowed to see.

### Community 24 - "Community 24"
Cohesion: 0.19
Nodes (15): _allowed_file(), create_leave(), delete_employee(), delete_leave(), delete_schedule(), edit_leave(), edit_schedule(), employees() (+7 more)

### Community 25 - "Community 25"
Cohesion: 0.18
Nodes (14): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), closeProjectSearch(), openCustomerSearch(), openProductSearch(), openProjectSearch(), renderCustomers() (+6 more)

### Community 26 - "Community 26"
Cohesion: 0.12
Nodes (15): dependencies, tailwindcss, devDependencies, concurrently, scripts, build, dev, i18n:all (+7 more)

### Community 27 - "Community 27"
Cohesion: 0.17
Nodes (5): bool, str, Contact, Validate phone format (basic: digits, +, -, spaces)., Validate email format.

### Community 29 - "Community 29"
Cohesion: 0.16
Nodes (5): int, post_invoice_payment_income(), Post a balanced income transaction for an invoice payment.      The transactio, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 30 - "Community 30"
Cohesion: 0.25
Nodes (10): int, float, int, DashboardService, DashboardService, Expense, ContactType, _recent_active_expenses() (+2 more)

### Community 31 - "Community 31"
Cohesion: 0.23
Nodes (11): Account, int, str, Transaction, _create_balanced_transaction(), Double-entry Balance Rules, Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if ent, Record an income / revenue event.          Double-entry:           DR  Cash / (+3 more)

### Community 32 - "Community 32"
Cohesion: 0.23
Nodes (10): int, str, Employee Editor Drawer, PTO Configuration, Employee Directory, Leave Request Form, leaves(), LeaveStatus (+2 more)

### Community 33 - "Community 33"
Cohesion: 0.19
Nodes (7): bool, str, Return True if the user's role carries *permission_name*.         Superadmins (r, Shortcut — True when the user's role is 'superadmin' (platform admin)., True when the user's role is 'owner' (company-level admin)., User, UserMixin

### Community 35 - "Community 35"
Cohesion: 0.20
Nodes (7): bool, float, str, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction

### Community 36 - "Community 36"
Cohesion: 0.20
Nodes (8): create(), delete(), edit(), index(), search_invoices(), store(), update(), view()

### Community 37 - "Community 37"
Cohesion: 0.36
Nodes (5): delete_account(), Account, int, Account CRUD and chart of accounts generation., Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 39 - "Community 39"
Cohesion: 0.31
Nodes (5): endpoint(), loadNotifications(), loadPopupNotifications(), notificationTypeClass(), showNotificationPopup()

### Community 40 - "Community 40"
Cohesion: 0.32
Nodes (8): Contact Directory, Contact Type Filtering, Contact Detail Screen, Customer Invoice History, Supplier Product History, Dashboard Quick Actions, ERP Summary Dashboard, Company Scoped Navigation

### Community 41 - "Community 41"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 42 - "Community 42"
Cohesion: 0.32
Nodes (3): Sends an error notification to the configured admin email., Sends a password reset email., send_password_reset()

### Community 43 - "Community 43"
Cohesion: 0.29
Nodes (4): float, str, Positive = debit effect, negative = credit effect., A single line in the accounting ledger.  Every entry MUST belong to a     Transa

### Community 44 - "Community 44"
Cohesion: 0.29
Nodes (4): float, str, create_schedule(), Total hours for this schedule entry.

### Community 45 - "Community 45"
Cohesion: 0.29
Nodes (5): create(), edit(), index(), store(), update()

### Community 46 - "Community 46"
Cohesion: 0.40
Nodes (4): bool, str, Return True if this role carries *permission_name*., Role

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

### Community 63 - "Community 63"
Cohesion: 0.67
Nodes (3): Python Application Dependencies, Flask Web Stack, PDF Excel Reporting Dependencies

## Knowledge Gaps
- **102 isolated node(s):** `Expense`, `Company`, `state`, `STATE_KEYS`, `history` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Flask` connect `Community 19` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 8`, `Community 9`, `Community 11`, `Community 12`, `Community 16`, `Community 18`, `Community 20`, `Community 21`, `Community 23`, `Community 24`, `Community 27`, `Community 29`, `Community 34`, `Community 36`, `Community 42`, `Community 45`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `Community 6` to `Community 0`, `Community 2`, `Community 5`, `Community 7`, `Community 9`, `Community 11`, `Community 16`, `Community 18`, `Community 20`, `Community 22`, `Community 27`, `Community 28`, `Community 32`, `Community 33`, `Community 35`, `Community 38`, `Community 43`, `Community 44`, `Community 46`, `Community 50`, `Community 54`, `Community 60`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `resolve_company()` connect `Community 12` to `Community 32`, `Community 1`, `Community 36`, `Community 37`, `Community 11`, `Community 44`, `Community 45`, `Community 19`, `Community 21`, `Community 22`, `Community 24`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `ProjectService` (e.g. with `Account` and `datetime`) actually correct?**
  _`ProjectService` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `AccountType` (e.g. with `int` and `str`) actually correct?**
  _`AccountType` has 37 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Manually log a change. Useful if automated listeners are not enough.`, `Helper to detect changed attributes and their values.`, `Registers global SQLAlchemy listeners for all models inheriting from Base.` to the rest of the system?**
  _217 weakly-connected nodes found - possible documentation gaps or missing edges._