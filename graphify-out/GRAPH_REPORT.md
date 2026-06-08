# Graph Report - flask-trackdesk  (2026-06-07)

## Corpus Check
- 142 files · ~110,090 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 828 nodes · 1691 edges · 64 communities (61 shown, 3 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 196 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8ee9b28e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Core Models|Core Models]]
- [[_COMMUNITY_App Init & Middleware|App Init & Middleware]]
- [[_COMMUNITY_Inventory & Orders Service|Inventory & Orders Service]]
- [[_COMMUNITY_Invoices Service|Invoices Service]]
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

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 91 edges
2. `AccountingService` - 38 edges
3. `int` - 35 edges
4. `str` - 32 edges
5. `Company` - 27 edges
6. `Document` - 25 edges
7. `AccountType` - 22 edges
8. `User` - 22 edges
9. `datetime` - 22 edges
10. `ExpenseStatus` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `Flask` --uses--> `Config`  [INFERRED]
  app/routes.py → config.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/purchase_order.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/ledger_entry.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/company.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/inventory/__init__.py -> app/inventory/__init__.py`
- 1-file cycle: `app/accounting/services/accounting_service.py -> app/accounting/services/accounting_service.py`
- 1-file cycle: `app/auth/__init__.py -> app/auth/__init__.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/routes.py -> app/routes.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/dashboard/__init__.py -> app/dashboard/__init__.py`
- 1-file cycle: `app/hr/__init__.py -> app/hr/__init__.py`
- 1-file cycle: `app/invoices/__init__.py -> app/invoices/__init__.py`
- 1-file cycle: `app/orders/__init__.py -> app/orders/__init__.py`
- 1-file cycle: `app/accounting/__init__.py -> app/accounting/__init__.py`
- 1-file cycle: `app.py -> app.py`
- 1-file cycle: `app/companies/__init__.py -> app/companies/__init__.py`
- 1-file cycle: `app/contacts/__init__.py -> app/contacts/__init__.py`
- 1-file cycle: `app/payments/__init__.py -> app/payments/__init__.py`
- 1-file cycle: `app/users/__init__.py -> app/users/__init__.py`
- 1-file cycle: `app/warehouses/__init__.py -> app/warehouses/__init__.py`

## Communities (64 total, 3 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.12
Nodes (10): str, str, str, str, AuditLog, BaseModel, UserStatus, Notification (+2 more)

### Community 1 - "App Init & Middleware"
Cohesion: 0.29
Nodes (9): Flask, register_context_processors(), get_locale(), register_extensions(), Flask, register_request_hooks(), Flask, register_routes() (+1 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.12
Nodes (29): chart_of_accounts(), create_account(), create_expense(), create_income(), create_journal_entry(), create_project(), create_tag(), delete_account() (+21 more)

### Community 3 - "Invoices Service"
Cohesion: 0.15
Nodes (11): float, str, Document, Calculate subtotal from document items (before tax). Cached., Calculate tax amount based on subtotal and company tax rate. Cached., Calculate total amount paid via payments, Calculate remaining balance to be paid, Calculate total discount amount from document items. Cached. (+3 more)

### Community 5 - "Community 5"
Cohesion: 0.36
Nodes (5): Flask, init_error_handlers(), init_rbac(), RBAC Middleware =============== Plugged into the app via ``init_rbac(app)`` in `, Register the RBAC ``before_request`` hook on *app*.

### Community 6 - "HR Module"
Cohesion: 0.05
Nodes (42): bool, float, str, int, str, float, str, bool (+34 more)

### Community 7 - "PDF Generators"
Cohesion: 0.13
Nodes (29): bool, float, str, int, str, str, Company, DocumentTemplate (+21 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.05
Nodes (22): api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_get_items(), api_search(), api_stats() (+14 more)

### Community 9 - "Auth Module"
Cohesion: 0.07
Nodes (16): float, int, bool, str, format_currency(), format_date(), locale_date(), Format a number as currency (+8 more)

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
Cohesion: 0.07
Nodes (11): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+3 more)

### Community 14 - "Companies Service"
Cohesion: 0.10
Nodes (22): str, str, str, BaseModel, Expense, Resolve vendor name from supplier relation or vendor_name field., Represents a business expense (outflow of money).      Income / revenue is recor, PurchaseOrderItem (+14 more)

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
Nodes (19): str, str, add_payment(), delete(), index(), print_invoice(), store(), update() (+11 more)

### Community 44 - "Community 44"
Cohesion: 0.25
Nodes (4): AuthService, Determine safe redirect URL after login., Generate and send a password reset token if user exists., Validate token and reset password.

### Community 45 - "Community 45"
Cohesion: 0.36
Nodes (6): register_cli(), str, Flask, Seed the database with default roles and their permissions.      Roles     -----, seed_default_roles_and_permissions(), Permission

### Community 46 - "Community 46"
Cohesion: 0.16
Nodes (7): int, AccountingService, Return a dict with:           account, all_accounts, opening_balance, ending_bal, Void old income transaction and create a corrected one., Void an income transaction (soft delete)., Soft-delete an account (set is_active=False, is_deleted=True, deleted_at=now)., Return full P&L breakdown for a project.

### Community 50 - "Community 50"
Cohesion: 0.32
Nodes (3): EmailService, Sends an error notification to the configured admin email., Sends a password reset email.

### Community 52 - "Community 52"
Cohesion: 0.15
Nodes (10): int, str, str, str, StockMovementType, InventoryItem, Return signed quantity: negative for outgoing, positive for incoming/adjustment., StockMovement (+2 more)

### Community 53 - "Community 53"
Cohesion: 0.23
Nodes (12): Account, int, str, Expense, AccountType, ExpenseStatus, Report, object (+4 more)

### Community 54 - "Community 54"
Cohesion: 0.21
Nodes (10): _create_balanced_transaction(), _parse_date(), Edit an existing expense.         Strategy: void the original transaction and cr, Create a Transaction + LedgerEntry rows atomically.     Raises ValueError if ent, Record an income / revenue event.          Double-entry:           DR  Cash / AR, Parse YYYY-MM-DD string → naive datetime. Falls back to now(UTC)., Manual multi-line journal entry.         Expects form fields: memo, date, refere, Void old manual multi-line journal entry and create a new one with updated data. (+2 more)

### Community 55 - "Community 55"
Cohesion: 0.17
Nodes (9): float, str, LedgerEntry, Positive = debit effect, negative = credit effect., A single line in the accounting ledger.  Every entry MUST belong to a     Transa, _allowed_file(), AccountingService — complete double-entry bookkeeping service.  Design rules (MU, Save uploaded receipt; return relative URL or None. (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.27
Nodes (9): datetime, float, _compute_account_balance(), _compute_balances_bulk(), _make_naive(), Compute balances for ALL accounts of a company in one query.     Returns {accoun, Strip timezone info so comparisons work with our stored naive datetimes., Compute the current balance of an account from LedgerEntry rows.      Normal bal (+1 more)

### Community 58 - "Community 58"
Cohesion: 0.23
Nodes (8): bool, float, str, TransactionType, Return True if total debits == total credits across all entries., Return the transaction amount (sum of debit side)., Groups one or more paired LedgerEntry rows into an atomic double-entry     journ, Transaction

### Community 59 - "Community 59"
Cohesion: 0.27
Nodes (4): Auto-generate a SKU from the item name and its DB id.                  Example:, _get_period_bounds(), Return (start_dt, end_dt) as naive datetimes for the given period., str

### Community 60 - "Community 60"
Cohesion: 0.22
Nodes (6): str, str, Account, Accounts that normally carry a debit balance vs credit balance., Chart of Accounts entry.      IMPORTANT: Balance is NOT stored here — it is alwa, DocumentSequence

### Community 61 - "Community 61"
Cohesion: 0.20
Nodes (7): AlchemyEncoder, AuditMiddleware, get_model_changes(), Registers global SQLAlchemy listeners for all models inheriting from Base., Manually log a change. Useful if automated listeners are not enough., Helper to detect changed attributes and their values., register_audit_listeners()

## Knowledge Gaps
- **22 isolated node(s):** `str`, `bool`, `float`, `state`, `STATE_KEYS` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseModel` connect `Core Models` to `Invoices Service`, `HR Module`, `PDF Generators`, `Auth Module`, `Users Service`, `Community 43`, `Community 45`, `Companies Service`, `Community 52`, `Community 53`, `Community 55`, `Community 60`, `Community 61`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `Company` connect `PDF Generators` to `Core Models`, `App Init & Middleware`, `Inventory & Orders Service`, `Invoices Service`, `Inventory Routes`, `Users Service`, `Companies Routes`, `Community 48`, `Community 55`, `Community 60`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `ContactType` connect `Auth Module` to `Core Models`, `Invoices Service`, `Inventory Routes`, `Community 43`, `Companies Routes`, `Companies Service`, `Community 60`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AccountingService` (e.g. with `AccountType` and `ExpenseStatus`) actually correct?**
  _`AccountingService` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `str` (e.g. with `EmployeeClass` and `LeaveStatus`) actually correct?**
  _`str` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Company` (e.g. with `bool` and `float`) actually correct?**
  _`Company` has 12 INFERRED edges - model-reasoned connections that need verification._