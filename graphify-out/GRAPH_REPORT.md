# Graph Report - .  (2026-06-03)

## Corpus Check
- 197 files · ~94,805 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 693 nodes · 1359 edges · 43 communities (42 shown, 1 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 175 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 95 edges
2. `Company` - 27 edges
3. `Document` - 25 edges
4. `AccountType` - 20 edges
5. `User` - 20 edges
6. `Contact` - 19 edges
7. `ContactType` - 18 edges
8. `CompanyService` - 17 edges
9. `InventoryItem` - 17 edges
10. `Report` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Flask` --uses--> `Config`  [INFERRED]
  app/context_processors.py → config.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/company.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_item.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_sequence.py → app/models/base.py
- `str` --uses--> `BaseModel`  [INFERRED]
  app/models/document_template.py → app/models/base.py

## Import Cycles
- 1-file cycle: `app.py -> app.py`
- 1-file cycle: `app/blueprints.py -> app/blueprints.py`
- 1-file cycle: `app/cli.py -> app/cli.py`
- 1-file cycle: `app/context_processors.py -> app/context_processors.py`
- 1-file cycle: `app/hooks.py -> app/hooks.py`
- 1-file cycle: `app/routes.py -> app/routes.py`
- 1-file cycle: `app/accounting/__init__.py -> app/accounting/__init__.py`
- 1-file cycle: `app/auth/__init__.py -> app/auth/__init__.py`
- 1-file cycle: `app/companies/__init__.py -> app/companies/__init__.py`
- 1-file cycle: `app/contacts/__init__.py -> app/contacts/__init__.py`
- 1-file cycle: `app/dashboard/__init__.py -> app/dashboard/__init__.py`
- 1-file cycle: `app/hr/__init__.py -> app/hr/__init__.py`
- 1-file cycle: `app/inventory/__init__.py -> app/inventory/__init__.py`
- 1-file cycle: `app/invoices/__init__.py -> app/invoices/__init__.py`
- 1-file cycle: `app/middleware/rbac.py -> app/middleware/rbac.py`
- 1-file cycle: `app/orders/__init__.py -> app/orders/__init__.py`
- 1-file cycle: `app/payments/__init__.py -> app/payments/__init__.py`
- 1-file cycle: `app/users/__init__.py -> app/users/__init__.py`
- 1-file cycle: `app/warehouses/__init__.py -> app/warehouses/__init__.py`

## Communities (43 total, 1 thin omitted)

### Community 0 - "Core Models"
Cohesion: 0.07
Nodes (26): str, str, str, str, str, str, str, str (+18 more)

### Community 1 - "App Init & Middleware"
Cohesion: 0.07
Nodes (30): Flask, register_blueprints(), Flask, register_cli(), Flask, register_context_processors(), get_locale(), register_extensions() (+22 more)

### Community 2 - "Inventory & Orders Service"
Cohesion: 0.06
Nodes (28): str, str, str, int, str, str, int, StockMovementType (+20 more)

### Community 3 - "Invoices Service"
Cohesion: 0.08
Nodes (29): str, float, str, str, add_payment(), delete(), index(), store() (+21 more)

### Community 4 - "Accounting Module"
Cohesion: 0.10
Nodes (16): Account, bool, int, str, str, Expense, AccountType, Report (+8 more)

### Community 5 - "Dashboard & Contacts"
Cohesion: 0.07
Nodes (16): float, int, bool, str, format_currency(), format_date(), locale_date(), Format a number as currency (+8 more)

### Community 6 - "HR Module"
Cohesion: 0.12
Nodes (29): bool, str, bool, float, str, int, str, _allowed_file() (+21 more)

### Community 7 - "PDF Generators"
Cohesion: 0.13
Nodes (30): bool, float, str, int, str, str, print_invoice(), Company (+22 more)

### Community 8 - "Inventory Routes"
Cohesion: 0.06
Nodes (20): api_adjust_stock(), api_bulk_delete(), api_create_item(), api_delete_item(), api_get_item(), api_get_items(), api_search(), api_stats() (+12 more)

### Community 9 - "Auth Module"
Cohesion: 0.09
Nodes (13): bool, str, bool, str, Return True if the user's role carries *permission_name*.         Superadmins (r, Shortcut — True when the user's role is 'superadmin' (platform admin)., True when the user's role is 'owner' (company-level admin)., Validate email format. (+5 more)

### Community 10 - "Users Service"
Cohesion: 0.09
Nodes (3): Returns IDs of companies the current user can see., Returns True if current_user can see/manage *user*., UserService

### Community 11 - "Barcode JS"
Cohesion: 0.14
Nodes (18): applyBarcodes(), buildBulkGrid(), buildLabelDOM(), buildPrintArea(), _doRender(), history, loadTemplates(), pushHistory() (+10 more)

### Community 12 - "Payments Module"
Cohesion: 0.09
Nodes (4): int, PaymentService, Recalculate and update the status of the invoice based on total payments., _recalculate_invoice_status()

### Community 13 - "Companies Routes"
Cohesion: 0.10
Nodes (10): List all document sequences for a company, Form to create a new document sequence, Store a new document sequence, Form to edit an existing document sequence, Update an existing document sequence, sequence_create(), sequence_edit(), sequence_store() (+2 more)

### Community 14 - "Companies Service"
Cohesion: 0.16
Nodes (3): str, DocumentSequence, CompanyService

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

## Knowledge Gaps
- **20 isolated node(s):** `bool`, `state`, `STATE_KEYS`, `history`, `zoomEl` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseModel` connect `Core Models` to `App Init & Middleware`, `Inventory & Orders Service`, `Invoices Service`, `Accounting Module`, `Dashboard & Contacts`, `HR Module`, `PDF Generators`, `Auth Module`, `Companies Service`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `Company` connect `PDF Generators` to `Core Models`, `App Init & Middleware`, `Invoices Service`, `Accounting Module`, `Inventory Routes`, `Users Service`, `Companies Service`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `ContactType` connect `Dashboard & Contacts` to `Core Models`, `Inventory & Orders Service`, `Invoices Service`, `Inventory Routes`, `Companies Service`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 66 inferred relationships involving `BaseModel` (e.g. with `str` and `str`) actually correct?**
  _`BaseModel` has 66 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Company` (e.g. with `bool` and `float`) actually correct?**
  _`Company` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Document` (e.g. with `BaseModel` and `Company`) actually correct?**
  _`Document` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `AccountType` (e.g. with `Account` and `bool`) actually correct?**
  _`AccountType` has 13 INFERRED edges - model-reasoned connections that need verification._