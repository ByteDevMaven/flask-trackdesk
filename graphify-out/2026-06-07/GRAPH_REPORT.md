# Graph Report - flask-trackdesk  (2026-06-07)

## Corpus Check
- 139 files · ~106,674 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 801 nodes · 1631 edges · 63 communities (60 shown, 3 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `268deca0`
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

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 92 edges
2. `AccountingService` - 38 edges
3. `int` - 34 edges
4. `Company` - 27 edges
5. `Document` - 25 edges
6. `User` - 22 edges
7. `AccountType` - 22 edges
8. `str` - 20 edges
9. `ExpenseStatus` - 20 edges
10. `datetime` - 19 edges

## Surprising Connections (you probably didn't know these)
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/purchase_order.py → app/models/base.py
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/ledger_entry.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/company.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_item.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/invoices/__init__.py -> app/invoices/__init__.py`
- 1-file cycle: `app/dashboard/__init__.py -> app/dashboard/__init__.py`
- 1-file cycle: `app/inventory/__init__.py -> app/inventory/__init__.py`
- 1-file cycle: `app/orders/__init__.py -> app/orders/__init__.py`
- 1-file cycle: `app/accounting/__init__.py -> app/accounting/__init__.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/hr/__init__.py -> app/hr/__init__.py`
- 1-file cycle: `app.py -> app.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/routes.py -> app/routes.py`
- 1-file cycle: `app/auth/__init__.py -> app/auth/__init__.py`
- 1-file cycle: `app/companies/__init__.py -> app/companies/__init__.py`
- 1-file cycle: `app/contacts/__init__.py -> app/contacts/__init__.py`
- 1-file cycle: `app/payments/__init__.py -> app/payments/__init__.py`
- 1-file cycle: `app/users/__init__.py -> app/users/__init__.py`
- 1-file cycle: `app/warehouses/__init__.py -> app/warehouses/__init__.py`

## Communities (63 total, 3 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.12
Nodes (12): str, str, str, str, str, AuditLog, BaseModel, DocumentSequence (+4 more)

### Community 1 - "App Init & Middleware"
Cohesion: 0.06
Nodes (34): Flask, register_blueprints(), Flask, register_cli(), Flask, register_context_processors(), get_locale(), register_extensions() (+26 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.12
Nodes (29): chart_of_accounts(), create_account(), create_expense(), create_income(), create_journal_entry(), create_project(), create_tag(), delete_account() (+21 more)

### Community 3 - "Invoices Service"
Cohesion: 0.25
Nodes (6): format_currency(), format_date(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale

### Community 4 - "Accounting Module"
Cohesion: 0.12
Nodes (14): bool, Return True if the user's role carries *permission_name*.         Superadmins (r, Validate email format., _allowed_file(), _get_period_bounds(), _parse_date(), Return a dict with:           account, all_accounts, opening_balance, ending_bal, Edit an existing expense.         Strategy: void the original transaction and cr (+6 more)

### Community 5 - "Dashboard & Contacts"
Cohesion: 0.27
Nodes (5): bool, str, Contact, Validate email format., Validate phone format (basic: digits, +, -, spaces).

### Community 6 - "HR Module"
Cohesion: 0.28
Nodes (11): bool, float, str, create_employee(), edit_employee(), Employee, Prefer the linked user's name when available., Deduct *days* from pto_balance if balance is sufficient. Returns True on success (+3 more)

### Community 7 - "PDF Generators"
Cohesion: 0.12
Nodes (31): bool, float, str, int, str, str, index(), Company (+23 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.05
Nodes (21): api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_get_items(), api_search(), api_stats() (+13 more)

### Community 10 - "Users Service"
Cohesion: 0.09
Nodes (3): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., UserService

### Community 11 - "Barcode JS"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 12 - "Payments Module"
Cohesion: 0.10
Nodes (4): int, PaymentService, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 13 - "Companies Routes"
Cohesion: 0.05
Nodes (19): bool, str, List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create() (+11 more)

### Community 14 - "Companies Service"
Cohesion: 0.14
Nodes (17): str, str, PurchaseOrderItem, PurchaseOrder, create(), delete(), export(), index() (+9 more)

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
Cohesion: 0.12
Nodes (16): str, str, add_payment(), delete(), print_invoice(), store(), update(), PaymentMethod (+8 more)

### Community 44 - "Community 44"
Cohesion: 0.15
Nodes (7): Document, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached., Calculate total amount paid via payments, Calculate remaining balance to be paid, Calculate total discount amount from document items. Cached., Refresh subtotal and tax caches

### Community 45 - "Community 45"
Cohesion: 0.17
Nodes (10): str, int, str, str, StockMovementType, InventoryItem, Return signed quantity: negative for outgoing, positive for incoming/adjustment., StockMovement (+2 more)

### Community 46 - "Community 46"
Cohesion: 0.16
Nodes (10): Account, int, AccountType, Project, AccountingService, Void old income transaction and create a corrected one., Void an income transaction (soft delete)., Soft-delete an account (set is_active=False, is_deleted=True, deleted_at=now). (+2 more)

### Community 48 - "Community 48"
Cohesion: 0.14
Nodes (14): float, str, _allowed_file(), create_leave(), create_schedule(), delete_employee(), delete_schedule(), edit_leave() (+6 more)

### Community 49 - "Community 49"
Cohesion: 0.24
Nodes (9): datetime, float, _compute_account_balance(), _compute_balances_bulk(), _make_naive(), AccountingService — complete double-entry bookkeeping service.  Design rules (MU, Compute balances for ALL accounts of a company in one query.     Returns {accoun, Strip timezone info so comparisons work with our stored naive datetimes. (+1 more)

### Community 52 - "Community 52"
Cohesion: 0.18
Nodes (9): str, str, BaseModel, Account, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa, Expense, Resolve vendor name from supplier relation or vendor_name field. (+1 more)

### Community 53 - "Community 53"
Cohesion: 0.23
Nodes (8): bool, float, str, TransactionType, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction

### Community 54 - "Community 54"
Cohesion: 0.25
Nodes (8): int, str, Expense, ExpenseStatus, Report, object, Response, Record an expense.          Double-entry:           DR  Expense Account       (a

### Community 55 - "Community 55"
Cohesion: 0.33
Nodes (7): int, str, leaves(), LeaveStatus, LeaveType, LeaveRequest, Calendar days of the leave (inclusive).

### Community 57 - "Community 57"
Cohesion: 0.24
Nodes (7): _create_balanced_transaction(), Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if ent, Record an income / revenue event.          Double-entry:           DR  Cash / AR, Manual multi-line journal entry.         Expects form fields: memo, date, refere, Void old manual multi-line journal entry and create a new one with updated data., Transaction, TransactionType

### Community 58 - "Community 58"
Cohesion: 0.33
Nodes (6): str, float, str, DocumentItem, DocumentStatus, DocumentType

### Community 60 - "Community 60"
Cohesion: 0.43
Nodes (4): float, int, ContactType, DashboardService

### Community 61 - "Community 61"
Cohesion: 0.29
Nodes (5): float, str, LedgerEntry, Positive = debit effect, negative = credit effect., A single line in the accounting ledger.  Every entry MUST belong to a     Transa

## Knowledge Gaps
- **23 isolated node(s):** `str`, `bool`, `float`, `bool`, `state` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseModel` connect `Core Models` to `App Init & Middleware`, `Dashboard & Contacts`, `HR Module`, `PDF Generators`, `Community 43`, `Community 44`, `Community 45`, `Companies Service`, `Companies Routes`, `Community 48`, `Community 52`, `Community 54`, `Community 55`, `Community 58`, `Community 61`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `Company` connect `PDF Generators` to `Core Models`, `App Init & Middleware`, `Inventory & Orders Service`, `Inventory Routes`, `Users Service`, `Community 44`, `Community 49`, `Community 50`, `Community 58`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `User` connect `Companies Routes` to `Core Models`, `App Init & Middleware`, `Accounting Module`, `Users Service`, `Community 48`, `Community 50`, `Community 52`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 63 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 63 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AccountingService` (e.g. with `AccountType` and `ExpenseStatus`) actually correct?**
  _`AccountingService` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Company` (e.g. with `bool` and `float`) actually correct?**
  _`Company` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Document` (e.g. with `BaseModel` and `Company`) actually correct?**
  _`Document` has 5 INFERRED edges - model-reasoned connections that need verification._