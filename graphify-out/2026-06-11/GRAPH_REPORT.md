# Graph Report - flask-trackdesk  (2026-06-11)

## Corpus Check
- 153 files · ~115,911 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 909 nodes · 2000 edges · 63 communities (62 shown, 1 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 196 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2135a9ee`
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
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 61|Community 61]]

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
- 1-file cycle: `app/accounting/__init__.py -> app/accounting/__init__.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/accounting/services/_balance.py -> app/accounting/services/_balance.py`
- 1-file cycle: `app/accounting/services/_helpers.py -> app/accounting/services/_helpers.py`
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

## Communities (63 total, 1 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.10
Nodes (16): str, str, str, str, str, int, str, str (+8 more)

### Community 1 - "App Init & Middleware"
Cohesion: 0.05
Nodes (31): Flask, register_blueprints(), register_cli(), register_context_processors(), get_locale(), register_extensions(), Flask, register_request_hooks() (+23 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.11
Nodes (37): chart_of_accounts(), _company_url_id(), create_account(), create_expense(), create_income(), create_journal_entry(), create_project(), create_tag() (+29 more)

### Community 3 - "Invoices Service"
Cohesion: 0.22
Nodes (11): bool, float, str, create_employee(), edit_employee(), Employee, Prefer the linked user's name when available., Deduct *days* from pto_balance if balance is sufficient. Returns True on success (+3 more)

### Community 4 - "Accounting Module"
Cohesion: 0.15
Nodes (32): Account, datetime, Expense, float, int, str, int, int (+24 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (35): Helper to resolve a company from a route parameter that could be an integer ID o, resolve_company(), api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_get_items() (+27 more)

### Community 6 - "HR Module"
Cohesion: 0.07
Nodes (16): Auto-generate a SKU from the item name and its DB id.                  Example:, Return True if the user's role carries *permission_name*.         Superadmins (r, Shortcut — True when the user's role is 'superadmin' (platform admin)., True when the user's role is 'owner' (company-level admin)., Validate email format., User, AuthService, Authenticate a user by email and password.         Returns (user, error_message) (+8 more)

### Community 7 - "PDF Generators"
Cohesion: 0.10
Nodes (32): bool, float, str, int, str, str, print_invoice(), Company (+24 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.16
Nodes (17): Account, int, Account, datetime, float, int, float, AccountService (+9 more)

### Community 9 - "Auth Module"
Cohesion: 0.31
Nodes (6): bool, str, Contact, Validate email format., Validate phone format (basic: digits, +, -, spaces)., ContactType

### Community 10 - "Users Service"
Cohesion: 0.09
Nodes (4): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., Returns the companies of target_user that current_user is allowed to see., UserService

### Community 11 - "Barcode JS"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 12 - "Payments Module"
Cohesion: 0.21
Nodes (6): int, str, LeaveStatus, UserStatus, LeaveRequest, Calendar days of the leave (inclusive).

### Community 13 - "Companies Routes"
Cohesion: 0.06
Nodes (12): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+4 more)

### Community 14 - "Companies Service"
Cohesion: 0.13
Nodes (17): str, bool, float, str, AccountType, ExpenseStatus, TransactionType, Report (+9 more)

### Community 15 - "NPM Config"
Cohesion: 0.12
Nodes (16): dependencies, tailwindcss, @tailwindcss/cli, devDependencies, concurrently, scripts, build, dev (+8 more)

### Community 16 - "Warehouses Service"
Cohesion: 0.27
Nodes (4): int, str, ProjectService, Return full P&L breakdown for a project.

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
Cohesion: 0.06
Nodes (31): str, str, int, add_payment(), delete(), index(), store(), update() (+23 more)

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (7): format_currency(), format_date(), index(), locale_date(), Format a number as currency, Format a date in a readable format, Format date according to the current locale

### Community 46 - "Community 46"
Cohesion: 0.29
Nodes (5): float, str, LedgerEntry, Positive = debit effect, negative = credit effect., A single line in the accounting ledger.  Every entry MUST belong to a     Transa

### Community 48 - "Community 48"
Cohesion: 0.27
Nodes (3): str, Warehouse, WarehouseService

### Community 49 - "Community 49"
Cohesion: 0.16
Nodes (10): int, str, _parse_journal_lines(), Parse and validate multi-line journal form data into entry dicts., Soft-delete a manual journal transaction., Return a full ledger page dict ready to pass to the template., Returns a trial balance as of a given date., Manual multi-line journal entry.         Expects form fields: memo, date, refere (+2 more)

### Community 50 - "Community 50"
Cohesion: 0.07
Nodes (27): str, str, str, BaseModel, InventoryItem, PurchaseOrderItem, PurchaseOrder, Return signed quantity: negative for outgoing, positive for incoming/adjustment. (+19 more)

### Community 52 - "Community 52"
Cohesion: 0.11
Nodes (24): bool, str, float, str, _allowed_file(), create_leave(), create_schedule(), delete_employee() (+16 more)

### Community 53 - "Community 53"
Cohesion: 0.11
Nodes (25): Transaction, Account, Expense, int, str, datetime, str, bool (+17 more)

### Community 54 - "Community 54"
Cohesion: 0.33
Nodes (4): str, Account, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa

### Community 55 - "Community 55"
Cohesion: 0.33
Nodes (4): str, Expense, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor

### Community 58 - "Community 58"
Cohesion: 0.29
Nodes (6): api_search(), create(), delete(), edit(), index(), view()

### Community 59 - "Community 59"
Cohesion: 0.23
Nodes (8): Account, int, str, Transaction, Record an income / revenue event.          Double-entry:           DR  Cash / AR, Void an income transaction (soft delete)., Void old income transaction and create a corrected one., _resolve_debit_account()

### Community 61 - "Community 61"
Cohesion: 0.33
Nodes (5): create(), edit(), index(), store(), update()

## Knowledge Gaps
- **31 isolated node(s):** `int`, `str`, `Expense`, `Account`, `Transaction` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Flask` connect `App Init & Middleware` to `Inventory & Orders Service`, `Accounting Module`, `Community 5`, `HR Module`, `Inventory Routes`, `Auth Module`, `Users Service`, `Community 43`, `Community 45`, `Community 50`, `Community 52`, `Community 53`, `Community 58`, `Community 61`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `Core Models` to `App Init & Middleware`, `Invoices Service`, `HR Module`, `PDF Generators`, `Auth Module`, `Community 43`, `Payments Module`, `Community 46`, `Companies Service`, `Community 48`, `Community 50`, `Community 52`, `Community 54`, `Community 55`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `resolve_company()` connect `Community 5` to `Inventory & Orders Service`, `Invoices Service`, `PDF Generators`, `Community 43`, `Community 45`, `Community 50`, `Community 52`, `Community 58`, `Community 61`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 60 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `Company` (e.g. with `bool` and `float`) actually correct?**
  _`Company` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Document` (e.g. with `BaseModel` and `Company`) actually correct?**
  _`Document` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `int`, `str`, `URL segment for company-scoped routes (slug preferred, else numeric id).` to the rest of the system?**
  _137 weakly-connected nodes found - possible documentation gaps or missing edges._