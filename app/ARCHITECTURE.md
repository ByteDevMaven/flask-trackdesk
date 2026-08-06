# Application structure

Each Flask feature owns its blueprint, templates, static assets, services, and route modules.

- `views/` contains thin HTTP handlers grouped by domain. A feature's legacy `routes.py` remains a small compatibility loader so blueprint imports stay stable.
- `services/` contains reusable business rules, validation, queries, and transaction boundaries.
- `templates/components/` contains shared Jinja UI and form primitives.
- `models/` contains persistence only; route-specific formatting belongs in services or template components.

Large blueprint splits:

- `accounting/views/`: dashboard, expenses, income, journal, accounts/reporting, projects, loans.
- `inventory/views/`: catalog, categories, movements, API, barcode.
- `hr/views/`: employees, leave, schedules, shared attachment helpers.
- `invoices/views/`: documents, payments/printing, document templates.
- `support/views/`: dashboard, audit, recovery, database browser, reflection helpers.
- `pos/services/pos_service.py`: numeric validation, stock payloads, receipts, register calculations, and checkout form construction.

Compatibility loaders must not contain business logic. New behavior should be added to the appropriate `views/` or `services/` module and covered by tests.