# Graph Report - flask-trackdesk  (2026-06-05)

## Corpus Check
- 137 files · ~105,394 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 796 nodes · 1626 edges · 57 communities (52 shown, 5 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 198 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `04324d52`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Core Models|Core Models]]
- [[_COMMUNITY_App Init & Middleware|App Init & Middleware]]
- [[_COMMUNITY_Inventory & Orders Service|Inventory & Orders Service]]
- [[_COMMUNITY_Invoices Service|Invoices Service]]
- [[_COMMUNITY_Accounting Module|Accounting Module]]
- [[_COMMUNITY_Dashboard & Contacts|Dashboard & Contacts]]
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
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 95 edges
2. `AccountingService` - 38 edges
3. `int` - 36 edges
4. `Company` - 27 edges
5. `Document` - 25 edges
6. `AccountType` - 24 edges
7. `ExpenseStatus` - 22 edges
8. `TransactionType` - 20 edges
9. `User` - 20 edges
10. `_is_ajax()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `bool` --uses--> `TransactionType`  [INFERRED]
  app/models/transaction.py → app/models/enums.py
- `float` --uses--> `TransactionType`  [INFERRED]
  app/models/transaction.py → app/models/enums.py
- `str` --uses--> `TransactionType`  [INFERRED]
  app/models/transaction.py → app/models/enums.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/ledger_entry.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/accounting/__init__.py -> app/accounting/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/hr/__init__.py -> app/hr/__init__.py`
- 1-file cycle: `app.py -> app.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/routes.py -> app/routes.py`
- 1-file cycle: `app/auth/__init__.py -> app/auth/__init__.py`
- 1-file cycle: `app/companies/__init__.py -> app/companies/__init__.py`
- 1-file cycle: `app/contacts/__init__.py -> app/contacts/__init__.py`
- 1-file cycle: `app/dashboard/__init__.py -> app/dashboard/__init__.py`
- 1-file cycle: `app/inventory/__init__.py -> app/inventory/__init__.py`
- 1-file cycle: `app/invoices/__init__.py -> app/invoices/__init__.py`
- 1-file cycle: `app/orders/__init__.py -> app/orders/__init__.py`
- 1-file cycle: `app/payments/__init__.py -> app/payments/__init__.py`
- 1-file cycle: `app/users/__init__.py -> app/users/__init__.py`
- 1-file cycle: `app/warehouses/__init__.py -> app/warehouses/__init__.py`

## Communities (57 total, 5 thin omitted)

### Community 1 - "App Init & Middleware"
Cohesion: 0.06
Nodes (38): Flask, register_blueprints(), Flask, register_cli(), Flask, register_context_processors(), get_locale(), register_extensions() (+30 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.12
Nodes (29): chart_of_accounts(), create_account(), create_expense(), create_income(), create_journal_entry(), create_project(), create_tag(), delete_account() (+21 more)

### Community 3 - "Invoices Service"
Cohesion: 0.15
Nodes (17): str, add_payment(), delete(), index(), print_invoice(), store(), update(), PaymentMethod (+9 more)

### Community 4 - "Accounting Module"
Cohesion: 0.06
Nodes (52): Account, int, bool, int, float, str, str, datetime (+44 more)

### Community 5 - "Dashboard & Contacts"
Cohesion: 0.06
Nodes (11): float, int, bool, str, Contact, Validate email format., Validate phone format (basic: digits, +, -, spaces)., ContactType (+3 more)

### Community 6 - "HR Module"
Cohesion: 0.13
Nodes (21): bool, float, str, bool, _allowed_file(), create_employee(), create_schedule(), delete_employee() (+13 more)

### Community 7 - "PDF Generators"
Cohesion: 0.13
Nodes (29): bool, float, str, int, str, str, Company, DocumentTemplate (+21 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.06
Nodes (20): api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_get_items(), api_search(), api_stats() (+12 more)

### Community 9 - "Auth Module"
Cohesion: 0.14
Nodes (3): str, InventoryItem, InventoryService

### Community 10 - "Users Service"
Cohesion: 0.08
Nodes (7): bool, str, Return True if this role carries *permission_name*., Role, Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., UserService

### Community 11 - "Barcode JS"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 12 - "Payments Module"
Cohesion: 0.10
Nodes (4): int, PaymentService, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 13 - "Companies Routes"
Cohesion: 0.10
Nodes (10): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+2 more)

### Community 14 - "Companies Service"
Cohesion: 0.17
Nodes (12): int, create(), delete(), export(), index(), update(), get_purchase_orders(), delete_purchase_order() (+4 more)

### Community 15 - "NPM Config"
Cohesion: 0.12
Nodes (16): dependencies, tailwindcss, @tailwindcss/cli, devDependencies, concurrently, scripts, build, dev (+8 more)

### Community 17 - "Invoice Form JS"
Cohesion: 0.26
Nodes (10): bindRowEvents(), closeCustomerSearch(), closeProductSearch(), openCustomerSearch(), openProductSearch(), renderCustomers(), renderProducts(), selectCustomer() (+2 more)

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
Nodes (11): str, int, str, str, StockMovementType, PurchaseOrderItem, Return signed quantity: negative for outgoing, positive for incoming/adjustment., StockMovement (+3 more)

### Community 44 - "Community 44"
Cohesion: 0.18
Nodes (9): str, str, BaseModel, Account, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa, Expense, Resolve vendor name from supplier relation or vendor_name field. (+1 more)

### Community 45 - "Community 45"
Cohesion: 0.29
Nodes (4): str, AuditMiddleware, Manually log a change. Useful if automated listeners are not enough., AuditLog

### Community 46 - "Community 46"
Cohesion: 0.09
Nodes (12): bool, str, bool, Return True if the user's role carries *permission_name*.         Superadmins (r, Shortcut — True when the user's role is 'superadmin' (platform admin)., True when the user's role is 'owner' (company-level admin)., Validate email format., User (+4 more)

### Community 47 - "Community 47"
Cohesion: 0.14
Nodes (12): str, str, str, str, str, str, BaseModel, Notification (+4 more)

### Community 49 - "Community 49"
Cohesion: 0.30
Nodes (8): int, str, create_leave(), leaves(), LeaveStatus, LeaveType, LeaveRequest, Calendar days of the leave (inclusive).

### Community 50 - "Community 50"
Cohesion: 0.29
Nodes (4): float, str, Total hours for this schedule entry., WorkSchedule

### Community 52 - "Community 52"
Cohesion: 0.18
Nodes (7): bool, float, str, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction

### Community 53 - "Community 53"
Cohesion: 0.25
Nodes (6): format_currency(), format_date(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale

## Knowledge Gaps
- **23 isolated node(s):** `bool`, `float`, `bool`, `bool`, `state` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseModel` connect `Community 47` to `Core Models`, `App Init & Middleware`, `Invoices Service`, `Accounting Module`, `Dashboard & Contacts`, `HR Module`, `PDF Generators`, `Auth Module`, `Users Service`, `Community 43`, `Community 44`, `Community 45`, `Community 46`, `Community 49`, `Community 50`, `Community 54`, `Community 55`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Why does `Company` connect `PDF Generators` to `Core Models`, `App Init & Middleware`, `Inventory & Orders Service`, `Accounting Module`, `Dashboard & Contacts`, `Inventory Routes`, `Users Service`, `Community 47`, `Community 48`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `ContactType` connect `Dashboard & Contacts` to `Inventory Routes`, `Core Models`, `Invoices Service`, `Companies Service`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 66 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 66 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AccountingService` (e.g. with `AccountType` and `ExpenseStatus`) actually correct?**
  _`AccountingService` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `int` (e.g. with `AccountType` and `ExpenseStatus`) actually correct?**
  _`int` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Company` (e.g. with `bool` and `float`) actually correct?**
  _`Company` has 12 INFERRED edges - model-reasoned connections that need verification._