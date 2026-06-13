# Graph Report - flask-trackdesk  (2026-06-12)

## Corpus Check
- 155 files · ~119,215 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1027 nodes · 2310 edges · 85 communities (74 shown, 11 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 319 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6bc175c1`
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
- [[_COMMUNITY_HR Migration|HR Migration]]
- [[_COMMUNITY_Login Migration|Login Migration]]
- [[_COMMUNITY_Tags Migration|Tags Migration]]
- [[_COMMUNITY_Modals UI JS|Modals UI JS]]
- [[_COMMUNITY_Flash UI JS|Flash UI JS]]
- [[_COMMUNITY_Index UI JS|Index UI JS]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]

## God Nodes (most connected - your core abstractions)
1. `resolve_company()` - 113 edges
2. `BaseModel` - 88 edges
3. `AccountType` - 51 edges
4. `Flask` - 50 edges
5. `TransactionType` - 40 edges
6. `Document` - 34 edges
7. `Company` - 28 edges
8. `ExpenseStatus` - 23 edges
9. `User` - 22 edges
10. `_create_balanced_transaction()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_item.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_template.py → app/models/base.py
- `int` --uses--> `BaseModel`  [INFERRED]
  app/models/inventory_item.py → app/models/base.py
- `float` --uses--> `BaseModel`  [INFERRED]
  app/models/ledger_entry.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/accounting/services/_balance.py -> app/accounting/services/_balance.py`
- 1-file cycle: `app/accounting/services/_helpers.py -> app/accounting/services/_helpers.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/routes.py -> app/routes.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`

## Hyperedges (group relationships)
- **Accounting Navigation Shell** — partials__nav_accounting_nav, accounting_dashboard_financial_command_center, accounting_expenses_screen, accounting_income_screen, accounting_journal_screen, accounting_ledger_screen, accounting_reports_screen, accounting_projects_screen [EXTRACTED 1.00]
- **Drawer Create Edit Forms** — partials_account_form_form, partials_expense_form_form, partials_income_form_form, partials_journal_form_form, partials_project_form_form, partials_tag_form_form [INFERRED 0.95]
- **Project Cost Center Flow** — accounting_projects_screen, accounting_project_detail_screen, partials_project_form_form, partials_expense_form_form, partials_income_form_form [INFERRED 0.95]
- **Company Fiscal Invoice Setup Flow** — companies_index_active_company_selector, companies_view_company_profile_dashboard, sequences_index_cai_sequence_registry, sequences_form_cai_authorization_form [EXTRACTED 1.00]
- **HR Leave And Schedule Review Flow** — hr_employees_employee_directory, hr_leave_requests_leave_request_queue, hr_leave_view_leave_review_panel, hr_schedules_work_schedule_calendar, hr_deviation_view_schedule_deviation_detail [INFERRED 0.85]
- **Inventory Stock Control Flow** — inventory_index_inventory_catalog, inventory_view_product_detail_screen, inventory_view_stock_distribution, inventory_drawer_adjust_stock_adjustment_form, inventory_drawer_transfer_stock_transfer_form, inventory_movements_stock_movement_ledger [EXTRACTED 1.00]
- **Financial Document Payment Flow** — view_invoice_detail_screen, form_payment_payment_form_screen, view_payment_payment_detail_screen, chunk_financial_document_payment_flow [EXTRACTED 1.00]
- **Shared Drawer Form Flow** — templates_base_shared_drawer, form_user_user_form_drawer, form_warehouse_warehouse_form_drawer, chunk_shared_drawer_form_pattern [EXTRACTED 1.00]
- **Operational Index Browse Flow** — index_invoice_document_list_screen, index_order_purchase_order_list_screen, index_payment_payment_list_screen, index_user_user_admin_list_screen, index_warehouse_warehouse_list_screen, chunk_shared_list_filter_pagination_pattern [EXTRACTED 1.00]

## Communities (85 total, 11 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.05
Nodes (35): bool, str, Flask, register_blueprints(), Flask, register_cli(), Flask, register_context_processors() (+27 more)

### Community 1 - "App Init & Middleware"
Cohesion: 0.11
Nodes (6): int, str, str, StockMovementType, Return signed quantity: negative for outgoing, positive for incoming/adjustment., Fetch an item by its SKU within a company.

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.09
Nodes (5): Sends a password reset email., Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., Returns the companies of target_user that current_user is allowed to see., send_password_reset()

### Community 3 - "Invoices Service"
Cohesion: 0.11
Nodes (13): str, str, str, str, str, str, str, str (+5 more)

### Community 4 - "Accounting Module"
Cohesion: 0.10
Nodes (22): Account Type Groups, Plan de Cuentas Screen, Centro de Mando Financiero, Accounting Dashboard KPIs, Recent Expenses Transactions Projects, Registrar Gasto Page, Nuevo Proyecto Page, Cost Center Profitability Management (+14 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (28): Financial Document Payment Flow, Shared List Filter Pagination Pattern, Invoice Client Picker Modal, Invoice Or Quote Document Form Screen, Invoice Embedded Form Data, Invoice Product And Item Editor, Invoice Optional Project Picker, Purchase Order Product Line Editor (+20 more)

### Community 6 - "HR Module"
Cohesion: 0.16
Nodes (18): str, str, add_payment(), delete(), index(), store(), update(), PaymentMethod (+10 more)

### Community 7 - "PDF Generators"
Cohesion: 0.10
Nodes (29): bool, float, str, int, str, str, print_invoice(), Company (+21 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.16
Nodes (11): float, str, Document, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached., Calculate total amount paid via payments, Calculate remaining balance to be paid, Calculate total discount amount from document items. Cached. (+3 more)

### Community 9 - "Auth Module"
Cohesion: 0.18
Nodes (11): int, str, _parse_journal_lines(), Journal entries, ledger, and trial balance service., Parse and validate multi-line journal form data into entry dicts., Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template., Returns a trial balance as of a given date. (+3 more)

### Community 10 - "Users Service"
Cohesion: 0.23
Nodes (9): Account, datetime, float, int, int, DashboardService, AccountingService — complete double-entry bookkeeping service.  This module re-e, Main AccountingService facade.     Inherits all @staticmethod methods from the d (+1 more)

### Community 11 - "Barcode JS"
Cohesion: 0.16
Nodes (7): float, bool, str, Contact, Validate phone format (basic: digits, +, -, spaces)., ContactType, Validate email format.

### Community 12 - "Payments Module"
Cohesion: 0.14
Nodes (27): int, str, Account, Expense, int, str, bool, datetime (+19 more)

### Community 13 - "Companies Routes"
Cohesion: 0.13
Nodes (26): Helper to resolve a company from a route parameter that could be an integer ID o, resolve_company(), api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_search() (+18 more)

### Community 14 - "Companies Service"
Cohesion: 0.16
Nodes (17): str, int, str, create(), delete(), edit(), export(), index() (+9 more)

### Community 15 - "NPM Config"
Cohesion: 0.21
Nodes (16): chart_of_accounts(), _company_url_id(), create_journal_entry(), edit_journal_entry(), expenses_list(), income_list(), journal_list(), ledger() (+8 more)

### Community 16 - "Warehouses Service"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+15 more)

### Community 17 - "Invoice Form JS"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 18 - "Migrations Core"
Cohesion: 0.17
Nodes (30): datetime, float, int, str, DashboardService, _active_expense_conditions(), _active_ledger_conditions(), _compute_account_balance() (+22 more)

### Community 19 - "Drawer UI JS"
Cohesion: 0.16
Nodes (21): create_account(), create_expense(), create_income(), create_project(), create_tag(), delete_account(), delete_expense(), delete_income() (+13 more)

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.08
Nodes (12): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+4 more)

### Community 21 - "Order Form JS"
Cohesion: 0.32
Nodes (8): Contact Directory, Contact Type Filtering, Contact Detail Screen, Customer Invoice History, Supplier Product History, Dashboard Quick Actions, ERP Summary Dashboard, Company Scoped Navigation

### Community 22 - "Unify Contacts Migration"
Cohesion: 0.20
Nodes (7): format_currency(), format_date(), index(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale

### Community 23 - "Auto Migration"
Cohesion: 0.18
Nodes (14): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), closeProjectSearch(), openCustomerSearch(), openProductSearch(), openProjectSearch(), renderCustomers() (+6 more)

### Community 24 - "Initial Migration"
Cohesion: 0.40
Nodes (3): int, str, Auto-generate a SKU from the item name and its DB id.                  Example:

### Community 25 - "Schedule Migration"
Cohesion: 0.12
Nodes (15): dependencies, tailwindcss, devDependencies, concurrently, scripts, build, dev, i18n:all (+7 more)

### Community 26 - "Audit Migration"
Cohesion: 0.26
Nodes (11): Account, int, str, Transaction, _create_balanced_transaction(), Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if ent, Income (revenue) CRUD service., Record an income / revenue event.          Double-entry:           DR  Cash / (+3 more)

### Community 27 - "Auto Migration 2"
Cohesion: 0.13
Nodes (20): Account, int, Account, Expense, int, Account, int, str (+12 more)

### Community 28 - "Doc Templates Migration"
Cohesion: 0.18
Nodes (3): int, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 29 - "Models Update Migration"
Cohesion: 0.20
Nodes (8): create(), delete(), edit(), index(), search_invoices(), store(), update(), view()

### Community 30 - "Audit Columns Migration"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 31 - "Roles Migration"
Cohesion: 0.29
Nodes (5): create(), edit(), index(), store(), update()

### Community 32 - "Warehouses Migration"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 33 - "Budget Migration"
Cohesion: 0.25
Nodes (6): api_search(), create(), delete(), edit(), index(), view()

### Community 34 - "Accounting Migration"
Cohesion: 0.50
Nodes (4): Stock Adjustment Form, Stock Transfer Form, Product Detail Screen, Warehouse Stock Distribution

### Community 35 - "HR Migration"
Cohesion: 0.40
Nodes (4): bool, str, Return True if this role carries *permission_name*., Role

### Community 36 - "Login Migration"
Cohesion: 0.06
Nodes (53): bool, str, bool, float, str, int, str, bool (+45 more)

### Community 38 - "Modals UI JS"
Cohesion: 0.47
Nodes (3): attachDrawerFormSubmit(), loadDrawerContent(), openDrawer()

### Community 39 - "Flash UI JS"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 40 - "Index UI JS"
Cohesion: 0.47
Nodes (3): _index_exists(), _table_exists(), upgrade()

### Community 44 - "Community 44"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "Community 45"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 46 - "Community 46"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 48 - "Community 48"
Cohesion: 0.20
Nodes (8): int, str, str, Company, Report, Project, ProjectService, Tag

### Community 52 - "Community 52"
Cohesion: 0.67
Nodes (3): Python Application Dependencies, Flask Web Stack, PDF Excel Reporting Dependencies

### Community 75 - "Community 75"
Cohesion: 0.10
Nodes (14): str, str, bool, float, str, BaseModel, Expense, Resolve vendor name from supplier relation or vendor_name field. (+6 more)

### Community 76 - "Community 76"
Cohesion: 0.83
Nodes (3): _column_exists(), downgrade(), upgrade()

## Knowledge Gaps
- **93 isolated node(s):** `Company`, `state`, `STATE_KEYS`, `history`, `zoomEl` (+88 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Flask` connect `Core Models` to `Inventory & Orders Service`, `HR Module`, `PDF Generators`, `Inventory Routes`, `Users Service`, `Barcode JS`, `Payments Module`, `Companies Routes`, `Companies Service`, `Migrations Core`, `Drawer UI JS`, `Consolidate Schema Migration`, `Unify Contacts Migration`, `Doc Templates Migration`, `Models Update Migration`, `Audit Columns Migration`, `Roles Migration`, `Budget Migration`, `Login Migration`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `Invoices Service` to `Core Models`, `App Init & Middleware`, `HR Migration`, `Login Migration`, `HR Module`, `PDF Generators`, `Inventory Routes`, `Auth Module`, `Barcode JS`, `Community 75`, `Community 43`, `Companies Service`, `Community 47`, `Community 48`, `Initial Migration`, `Auto Migration 2`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `resolve_company()` connect `Companies Routes` to `Budget Migration`, `Login Migration`, `HR Module`, `PDF Generators`, `Companies Service`, `NPM Config`, `Drawer UI JS`, `Unify Contacts Migration`, `Models Update Migration`, `Roles Migration`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `AccountType` (e.g. with `int` and `str`) actually correct?**
  _`AccountType` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `TransactionType` (e.g. with `int` and `str`) actually correct?**
  _`TransactionType` has 34 INFERRED edges - model-reasoned connections that need verification._
- **What connects `URL segment for company-scoped routes (slug preferred, else numeric id).`, `Company`, `Project CRUD, tagging, and reporting service.` to the rest of the system?**
  _202 weakly-connected nodes found - possible documentation gaps or missing edges._