from flask import Flask, request, session, redirect, url_for, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from config import Config
from app.models import Contact, Document, InventoryItem, PurchaseOrder, Company, Payment, Project, Expense, Warehouse


SEARCH_CATEGORIES = (
    ('best_matches', 'Mejores resultados', 'Resultados con mayor coincidencia en todos los modulos.'),
    ('contacts', 'Contactos', 'Clientes, proveedores y leads.'),
    ('documents', 'Facturas y documentos', 'Facturas, cotizaciones, notas y estados.'),
    ('inventory_items', 'Inventario', 'Productos, SKU, descripciones y proveedores.'),
    ('purchase_orders', 'Ordenes de compra', 'Ordenes, proveedores y documentos.'),
    ('payments', 'Pagos', 'Pagos, facturas relacionadas y notas.'),
    ('projects', 'Proyectos', 'Proyectos, estado y descripcion.'),
    ('expenses', 'Gastos', 'Gastos, proveedor, categoria y descripcion.'),
    ('warehouses', 'Almacenes', 'Bodegas y ubicaciones.'),
    ('companies', 'Empresas', 'Empresas disponibles para tu usuario.'),
)


def _search_tokens(query_text):
    return [token.lower() for token in query_text.split() if token.strip()]


def _field_values(*values):
    return [str(value) for value in values if value not in (None, '')]


def _match_context(query_text, weighted_fields):
    query = query_text.lower()
    tokens = _search_tokens(query_text)
    score = 0
    matched_labels = []

    for label, value, weight in weighted_fields:
        text = str(value or '').strip()
        if not text:
            continue

        lowered = text.lower()
        if lowered == query:
            score += weight * 5
            matched_labels.append(label)
        elif lowered.startswith(query):
            score += weight * 3
            matched_labels.append(label)
        elif query in lowered:
            score += weight * 2
            matched_labels.append(label)
        else:
            token_hits = sum(1 for token in tokens if token in lowered)
            if token_hits:
                score += weight * token_hits
                matched_labels.append(label)

    return score, list(dict.fromkeys(matched_labels))


def _result(kind, title, subtitle, url, query_text, fields, meta=None):
    score, matched_fields = _match_context(query_text, fields)
    return {
        'kind': kind,
        'title': title,
        'subtitle': subtitle,
        'url': url,
        'score': score,
        'matched_fields': matched_fields,
        'meta': meta or [],
    }


def _enum_label(value):
    return getattr(value, 'value', value)


def _money(value):
    try:
        return f"{float(value or 0):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _selected_company_scope():
    selected_company_id = session.get('selected_company_id')
    user_company_ids = [company.id for company in current_user.companies]
    if selected_company_id in user_company_ids:
        return [selected_company_id]
    return user_company_ids


def register_routes(app: Flask):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index', company_id=session.get('selected_company_slug')))
        return render_template('public/landing.html')

    @app.route('/set-company/<int:id>')
    def set_company(id):
        if not current_user.is_authenticated:
            abort(401)
        for company in current_user.companies:
            if company.id == id:
                session['selected_company_id'] = id
                session['selected_company_slug'] = company.slug
                session['currency'] = company.currency
                session['tax_rate'] = float(company.tax_rate) if company.tax_rate else 0.0
                app.logger.info(f"Tax rate: {session.get('tax_rate', 0)}%")
                break
        return redirect(url_for('dashboard.index', company_id=session.get('selected_company_slug')))

    @app.route('/set-language/<language>')
    def set_language(language):
        if language in Config.LANGUAGES:
            session['language'] = language
        return redirect(request.referrer or url_for('dashboard.index'))

    @app.route('/search')
    @login_required
    def search():
        query_text = request.args.get('q', '').strip()
        category_filter = request.args.get('type', 'all').strip() or 'all'
        valid_categories = {key for key, _, _ in SEARCH_CATEGORIES}
        if category_filter not in valid_categories and category_filter != 'all':
            category_filter = 'all'
        company_ids = _selected_company_scope()
        results = {key: [] for key, _, _ in SEARCH_CATEGORIES}

        if query_text:
            search_term = f"%{query_text}%"

            contacts = Contact.query.filter(Contact.company_id.in_(company_ids)).filter(
                or_(
                    Contact.name.ilike(search_term),
                    Contact.legal_name.ilike(search_term),
                    Contact.email.ilike(search_term),
                    Contact.identifier.ilike(search_term),
                    Contact.phone.ilike(search_term),
                    Contact.notes.ilike(search_term),
                )
            ).order_by(Contact.name).limit(15).all()
            results['contacts'] = [
                _result(
                    'Contactos',
                    c.name,
                    ' - '.join(_field_values(c.type.name.replace('_', ' ').title(), c.email or c.phone or c.identifier)),
                    url_for('contacts.view', company_id=c.company_id, contact_id=c.id),
                    query_text,
                    (
                        ('Nombre', c.name, 5),
                        ('Nombre legal', c.legal_name, 4),
                        ('RTN/ID', c.identifier, 5),
                        ('Correo', c.email, 4),
                        ('Telefono', c.phone, 3),
                        ('Notas', c.notes, 1),
                    ),
                    ['Cliente/proveedor'],
                )
                for c in contacts
            ]

            documents = Document.query.outerjoin(Document.client).filter(Document.company_id.in_(company_ids)).filter(
                or_(
                    Document.document_number.ilike(search_term),
                    Document.status.ilike(search_term),
                    Document.type.ilike(search_term),
                    Contact.name.ilike(search_term),
                    Contact.identifier.ilike(search_term),
                )
            ).order_by(Document.issued_date.desc()).limit(15).all()
            results['documents'] = [
                _result(
                    'Facturas',
                    d.document_number,
                    ' - '.join(_field_values(_enum_label(d.type).title(), _enum_label(d.status).title(), d.client.name if d.client else None)),
                    url_for('invoices.view', company_id=d.company_id, id=d.id),
                    query_text,
                    (
                        ('Numero', d.document_number, 6),
                        ('Estado', _enum_label(d.status), 3),
                        ('Tipo', _enum_label(d.type), 2),
                        ('Cliente', d.client.name if d.client else '', 5),
                        ('RTN/ID cliente', d.client.identifier if d.client else '', 4),
                    ),
                    [f"Total {_money(d.total_amount)}", d.issued_date.strftime('%d/%m/%Y') if d.issued_date else 'Sin fecha'],
                )
                for d in documents
            ]

            inventory_items = InventoryItem.query.outerjoin(InventoryItem.supplier).filter(InventoryItem.company_id.in_(company_ids)).filter(
                or_(
                    InventoryItem.sku.ilike(search_term),
                    InventoryItem.name.ilike(search_term),
                    InventoryItem.description.ilike(search_term),
                    Contact.name.ilike(search_term),
                )
            ).order_by(InventoryItem.name).limit(15).all()
            results['inventory_items'] = [
                _result(
                    'Inventario',
                    i.name,
                    ' - '.join(_field_values(i.sku, i.description, i.supplier.name if i.supplier else None)),
                    url_for('inventory.view', company_id=i.company_id, sku=i.sku) if i.sku else url_for('inventory.index', company_id=i.company_id, search=i.name),
                    query_text,
                    (
                        ('SKU', i.sku, 6),
                        ('Producto', i.name, 5),
                        ('Descripcion', i.description, 2),
                        ('Proveedor', i.supplier.name if i.supplier else '', 4),
                    ),
                    [f"Stock {i.quantity}", f"Precio {_money(i.price)}"],
                )
                for i in inventory_items
            ]

            purchase_orders = PurchaseOrder.query.outerjoin(PurchaseOrder.supplier).filter(PurchaseOrder.company_id.in_(company_ids)).filter(
                or_(
                    PurchaseOrder.order_number.ilike(search_term),
                    PurchaseOrder.order_document.ilike(search_term),
                    Contact.name.ilike(search_term),
                    Contact.identifier.ilike(search_term),
                )
            ).order_by(PurchaseOrder.buy_date.desc()).limit(15).all()
            results['purchase_orders'] = [
                _result(
                    'Ordenes de compra',
                    p.order_number,
                    ' - '.join(_field_values(p.supplier.name if p.supplier else None, p.buy_date.strftime('%d/%m/%Y') if p.buy_date else None)),
                    url_for('orders.view', company_id=p.company_id, id=p.id),
                    query_text,
                    (
                        ('Numero', p.order_number, 6),
                        ('Documento', p.order_document, 4),
                        ('Proveedor', p.supplier.name if p.supplier else '', 5),
                        ('RTN/ID proveedor', p.supplier.identifier if p.supplier else '', 4),
                    ),
                    [f"Total {_money(p.total_amount)}"],
                )
                for p in purchase_orders
            ]

            payments = Payment.query.outerjoin(Payment.document).outerjoin(Document.client).filter(Payment.company_id.in_(company_ids)).filter(
                or_(
                    Payment.notes.ilike(search_term),
                    Payment.method.ilike(search_term),
                    Document.document_number.ilike(search_term),
                    Contact.name.ilike(search_term),
                    Contact.identifier.ilike(search_term),
                )
            ).order_by(Payment.payment_date.desc()).limit(15).all()
            results['payments'] = [
                _result(
                    'Pagos',
                    f"Pago #{p.id}",
                    ' - '.join(_field_values(p.document.document_number if p.document else None, p.document.client.name if p.document and p.document.client else None, _enum_label(p.method).title())),
                    url_for('payments.view', company_id=p.company_id, id=p.id),
                    query_text,
                    (
                        ('Notas', p.notes, 2),
                        ('Metodo', _enum_label(p.method), 3),
                        ('Factura', p.document.document_number if p.document else '', 6),
                        ('Cliente', p.document.client.name if p.document and p.document.client else '', 5),
                        ('RTN/ID cliente', p.document.client.identifier if p.document and p.document.client else '', 4),
                    ),
                    [f"Monto {_money(p.amount)}", p.payment_date.strftime('%d/%m/%Y') if p.payment_date else 'Sin fecha'],
                )
                for p in payments
            ]

            projects = Project.query.filter(Project.company_id.in_(company_ids)).filter(
                or_(
                    Project.name.ilike(search_term),
                    Project.description.ilike(search_term),
                    Project.status.ilike(search_term),
                )
            ).order_by(Project.name).limit(15).all()
            results['projects'] = [
                _result(
                    'Proyectos',
                    p.name,
                    ' - '.join(_field_values(p.status.title() if p.status else None, p.description)),
                    url_for('accounting.project_detail', company_id=p.company_id, project_id=p.id),
                    query_text,
                    (
                        ('Proyecto', p.name, 6),
                        ('Estado', p.status, 3),
                        ('Descripcion', p.description, 2),
                    ),
                    [f"Presupuesto {_money(p.budget)}"],
                )
                for p in projects
            ]

            expenses = Expense.query.outerjoin(Expense.supplier).filter(Expense.company_id.in_(company_ids)).filter(
                or_(
                    Expense.description.ilike(search_term),
                    Expense.vendor_name.ilike(search_term),
                    Expense.category.ilike(search_term),
                    Expense.status.ilike(search_term),
                    Contact.name.ilike(search_term),
                    Contact.identifier.ilike(search_term),
                )
            ).order_by(Expense.date.desc()).limit(15).all()
            results['expenses'] = [
                _result(
                    'Gastos',
                    e.description or f"Gasto #{e.id}",
                    ' - '.join(_field_values(e.vendor_display, e.category, _enum_label(e.status).title())),
                    url_for('accounting.edit_expense', company_id=e.company_id, expense_id=e.id),
                    query_text,
                    (
                        ('Descripcion', e.description, 5),
                        ('Proveedor', e.vendor_display, 5),
                        ('Categoria', e.category, 4),
                        ('Estado', _enum_label(e.status), 3),
                        ('RTN/ID proveedor', e.supplier.identifier if e.supplier else '', 4),
                    ),
                    [f"Monto {_money(e.amount)}", e.date.strftime('%d/%m/%Y') if e.date else 'Sin fecha'],
                )
                for e in expenses
            ]

            warehouses = Warehouse.query.filter(Warehouse.company_id.in_(company_ids)).filter(
                or_(
                    Warehouse.name.ilike(search_term),
                    Warehouse.location.ilike(search_term),
                )
            ).order_by(Warehouse.name).limit(15).all()
            results['warehouses'] = [
                _result(
                    'Almacenes',
                    w.name,
                    w.location or '',
                    url_for('warehouses.index', company_id=w.company_id, search=w.name),
                    query_text,
                    (
                        ('Almacen', w.name, 6),
                        ('Ubicacion', w.location, 4),
                    ),
                    ['Activo' if w.is_active else 'Inactivo'],
                )
                for w in warehouses
            ]

            company_results = Company.query.filter(Company.id.in_([c.id for c in current_user.companies])).filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.identifier.ilike(search_term),
                    Company.email.ilike(search_term),
                    Company.phone.ilike(search_term),
                    Company.address.ilike(search_term),
                )
            ).order_by(Company.name).limit(15).all()
            results['companies'] = [
                _result(
                    'Empresas',
                    c.name,
                    ' - '.join(_field_values(c.identifier, c.email or c.phone)),
                    url_for('companies.view', id=c.id),
                    query_text,
                    (
                        ('Empresa', c.name, 6),
                        ('RTN/ID', c.identifier, 5),
                        ('Correo', c.email, 4),
                        ('Telefono', c.phone, 3),
                        ('Direccion', c.address, 2),
                    ),
                    [c.currency, c.timezone],
                )
                for c in company_results
            ]

            for key in results:
                if key != 'best_matches':
                    results[key] = sorted(results[key], key=lambda item: (-item['score'], item['title'].lower()))

            all_matches = [item for key, items in results.items() if key != 'best_matches' for item in items]
            results['best_matches'] = sorted(all_matches, key=lambda item: (-item['score'], item['title'].lower()))[:12]

        category_meta = [
            {
                'key': key,
                'label': label,
                'description': description,
                'count': len(results.get(key, [])),
            }
            for key, label, description in SEARCH_CATEGORIES
        ]
        visible_categories = [category for category in category_meta if category_filter in ('all', category['key'])]
        total_results = sum(len(results.get(key, [])) for key, _, _ in SEARCH_CATEGORIES if key != 'best_matches')

        return render_template(
            'search/results.html',
            query=query_text,
            results=results,
            categories=category_meta,
            visible_categories=visible_categories,
            active_type=category_filter,
            total_results=total_results,
        )
