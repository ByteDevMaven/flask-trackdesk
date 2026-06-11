# Graph Report - flask-trackdesk  (2026-06-10)

## Corpus Check
- 153 files · ~115,583 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 906 nodes · 1996 edges · 69 communities (65 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 198 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `29689f0d`
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
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]

## God Nodes (most connected - your core abstractions)
1. `resolve_company()` - 114 edges
2. `BaseModel` - 89 edges
3. `Flask` - 29 edges
4. `Company` - 27 edges
5. `Document` - 26 edges
6. `User` - 22 edges
7. `_is_ajax()` - 20 edges
8. `str` - 20 edges
9. `InventoryItem` - 19 edges
10. `Contact` - 19 edges

## Surprising Connections (you probably didn't know these)
- `float` --uses--> `ContactType`  [INFERRED]
  app/dashboard/services/dashboard_service.py → app/models/enums.py
- `int` --uses--> `ContactType`  [INFERRED]
  app/dashboard/services/dashboard_service.py → app/models/enums.py
- `Flask` --uses--> `Config`  [INFERRED]
  app/routes.py → config.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/purchase_order.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/ledger_entry.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/accounting/services/_balance.py -> app/accounting/services/_balance.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/accounting/services/_helpers.py -> app/accounting/services/_helpers.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/accounting/__init__.py -> app/accounting/__init__.py`
- 1-file cycle: `app/invoices/__init__.py -> app/invoices/__init__.py`
- 1-file cycle: `app/users/__init__.py -> app/users/__init__.py`
- 1-file cycle: `app/contacts/__init__.py -> app/contacts/__init__.py`
- 1-file cycle: `app/dashboard/__init__.py -> app/dashboard/__init__.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/hr/__init__.py -> app/hr/__init__.py`
- 1-file cycle: `app/inventory/__init__.py -> app/inventory/__init__.py`
- 1-file cycle: `app/orders/__init__.py -> app/orders/__init__.py`
- 1-file cycle: `app/payments/__init__.py -> app/payments/__init__.py`
- 1-file cycle: `app/routes.py -> app/routes.py`
- 1-file cycle: `app/warehouses/__init__.py -> app/warehouses/__init__.py`
- 1-file cycle: `app/auth/__init__.py -> app/auth/__init__.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app.py -> app.py`
- 1-file cycle: `app/companies/__init__.py -> app/companies/__init__.py`

## Communities (69 total, 4 thin omitted)

### Community 1 - "App Init & Middleware"
Cohesion: 0.07
Nodes (27): Flask, register_blueprints(), register_cli(), register_context_processors(), get_locale(), register_extensions(), Flask, register_request_hooks() (+19 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.16
Nodes (21): create_account(), create_expense(), create_income(), create_journal_entry(), create_project(), create_tag(), delete_account(), delete_expense() (+13 more)

### Community 3 - "Invoices Service"
Cohesion: 0.10
Nodes (9): int, str, str, StockMovementType, Return signed quantity: negative for outgoing, positive for incoming/adjustment., StockMovement, WarehouseItem, InventoryService (+1 more)

### Community 4 - "Accounting Module"
Cohesion: 0.14
Nodes (31): Account, datetime, Expense, float, int, str, int, int (+23 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (31): Helper to resolve a company from a route parameter that could be an integer ID o, resolve_company(), schedule_events(), schedules(), view_deviation(), view_leave(), api_adjust_stock(), api_bulk_delete() (+23 more)

### Community 6 - "HR Module"
Cohesion: 0.05
Nodes (42): bool, str, bool, float, str, int, str, _allowed_file() (+34 more)

### Community 7 - "PDF Generators"
Cohesion: 0.10
Nodes (32): bool, float, str, int, str, str, print_invoice(), Company (+24 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.12
Nodes (21): Account, datetime, float, int, int, str, float, AccountType (+13 more)

### Community 9 - "Auth Module"
Cohesion: 0.16
Nodes (8): bool, str, Contact, Validate email format., Validate phone format (basic: digits, +, -, spaces)., ContactType, InventoryItem, ContactService

### Community 10 - "Users Service"
Cohesion: 0.09
Nodes (4): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., Returns the companies of target_user that current_user is allowed to see., UserService

### Community 11 - "Barcode JS"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 12 - "Payments Module"
Cohesion: 0.24
Nodes (13): chart_of_accounts(), expenses_list(), income_list(), journal_list(), ledger(), project_detail(), projects_list(), reports() (+5 more)

### Community 13 - "Companies Routes"
Cohesion: 0.06
Nodes (12): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+4 more)

### Community 14 - "Companies Service"
Cohesion: 0.21
Nodes (8): bool, float, str, TransactionType, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction

### Community 15 - "NPM Config"
Cohesion: 0.12
Nodes (16): dependencies, tailwindcss, @tailwindcss/cli, devDependencies, concurrently, scripts, build, dev (+8 more)

### Community 16 - "Warehouses Service"
Cohesion: 0.18
Nodes (4): int, PaymentService, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 17 - "Invoice Form JS"
Cohesion: 0.18
Nodes (14): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), closeProjectSearch(), openCustomerSearch(), openProductSearch(), openProjectSearch(), renderCustomers() (+6 more)

### Community 18 - "Migrations Core"
Cohesion: 0.39
Nodes (7): get_engine(), get_engine_url(), get_metadata(), Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 19 - "Drawer UI JS"
Cohesion: 0.47
Nodes (3): attachDrawerFormSubmit(), loadDrawerContent(), openDrawer()

### Community 20 - "Consolidate Schema Migration"
Cohesion: 0.47
Nodes (3): _index_exists(), _table_exists(), upgrade()

### Community 43 - "Community 43"
Cohesion: 0.18
Nodes (17): str, add_payment(), delete(), index(), store(), update(), DocumentItem, PaymentMethod (+9 more)

### Community 44 - "Community 44"
Cohesion: 0.18
Nodes (7): str, AlchemyEncoder, AuditMiddleware, get_model_changes(), Manually log a change. Useful if automated listeners are not enough., Helper to detect changed attributes and their values., AuditLog

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (7): format_currency(), format_date(), index(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale

### Community 46 - "Community 46"
Cohesion: 0.25
Nodes (5): float, str, LedgerEntry, Positive = debit effect, negative = credit effect., A single line in the accounting ledger.  Every entry MUST belong to a     Transa

### Community 48 - "Community 48"
Cohesion: 0.11
Nodes (4): str, Warehouse, WarehouseService, WarehouseServiceTestCase

### Community 49 - "Community 49"
Cohesion: 0.13
Nodes (21): datetime, int, str, Transaction, _get_period_bounds(), _make_naive(), _parse_date(), Internal date / file helpers shared across accounting services. (+13 more)

### Community 50 - "Community 50"
Cohesion: 0.14
Nodes (19): str, str, PurchaseOrderItem, PurchaseOrder, create(), delete(), edit(), export() (+11 more)

### Community 52 - "Community 52"
Cohesion: 0.12
Nodes (13): str, str, str, str, float, str, BaseModel, DocumentSequence (+5 more)

### Community 53 - "Community 53"
Cohesion: 0.12
Nodes (18): Transaction, Account, Expense, int, str, str, bool, _create_balanced_transaction() (+10 more)

### Community 54 - "Community 54"
Cohesion: 0.18
Nodes (9): str, str, BaseModel, Account, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa, Expense, Resolve vendor name from supplier relation or vendor_name field. (+1 more)

### Community 55 - "Community 55"
Cohesion: 0.22
Nodes (8): create(), delete(), edit(), index(), search_invoices(), store(), update(), view()

### Community 58 - "Community 58"
Cohesion: 0.29
Nodes (6): api_search(), create(), delete(), edit(), index(), view()

### Community 59 - "Community 59"
Cohesion: 0.23
Nodes (8): Account, int, str, Transaction, Record an income / revenue event.          Double-entry:           DR  Cash / AR, Void an income transaction (soft delete)., Void old income transaction and create a corrected one., _resolve_debit_account()

### Community 60 - "Community 60"
Cohesion: 0.43
Nodes (4): Account, int, AccountService, Soft-delete an account.         Raises ValueError if the account has any non-voi

### Community 61 - "Community 61"
Cohesion: 0.33
Nodes (5): create(), edit(), index(), store(), update()

### Community 65 - "Community 65"
Cohesion: 0.40
Nodes (4): bool, str, Return True if this role carries *permission_name*., Role

### Community 66 - "Community 66"
Cohesion: 0.15
Nodes (9): Document, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached., Calculate total amount paid via payments, Calculate remaining balance to be paid, Calculate total discount amount from document items. Cached., Refresh subtotal and tax caches, DocumentStatus (+1 more)

## Knowledge Gaps
- **29 isolated node(s):** `Expense`, `Account`, `Transaction`, `int`, `str` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Flask` connect `App Init & Middleware` to `Inventory & Orders Service`, `Accounting Module`, `Community 5`, `HR Module`, `Inventory Routes`, `Auth Module`, `Users Service`, `Community 43`, `Community 45`, `Community 49`, `Community 50`, `Community 55`, `Community 58`, `Community 61`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `Community 52` to `Community 64`, `Community 65`, `Core Models`, `Community 67`, `Invoices Service`, `Community 66`, `HR Module`, `PDF Generators`, `Auth Module`, `Community 43`, `Community 44`, `Community 46`, `Community 48`, `Community 50`, `Community 54`, `Community 57`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `resolve_company()` connect `Community 5` to `Inventory & Orders Service`, `HR Module`, `PDF Generators`, `Community 43`, `Payments Module`, `Community 45`, `Community 50`, `Community 55`, `Community 58`, `Community 61`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 60 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `Company` (e.g. with `bool` and `float`) actually correct?**
  _`Company` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Document` (e.g. with `BaseModel` and `Company`) actually correct?**
  _`Document` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Expense`, `Account`, `Transaction` to the rest of the system?**
  _134 weakly-connected nodes found - possible documentation gaps or missing edges._