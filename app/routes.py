from flask import Flask, request, session, redirect, url_for, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from config import Config
from app.models import Contact, Document, InventoryItem, PurchaseOrder, Company

def register_routes(app: Flask):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # Safely get the company_id; if none, it'll redirect to the first company's dashboard usually via dashboard routes
            return redirect(url_for('dashboard.index', company_id=session.get('selected_company_id')))
        return render_template('public/landing.html')

    @app.route('/set-company/<int:id>')
    def set_company(id):
        if not current_user.is_authenticated:
            abort(401)
        for company in current_user.companies:
            if company.id == id:
                session['selected_company_id'] = id
                session['currency'] = company.currency
                session['tax_rate'] = company.tax_rate
                app.logger.info(f"Tax rate: {session.get('tax_rate', 0)}%")
                break
        return redirect(url_for('dashboard.index', company_id=session.get('selected_company_id')))

    @app.route('/set-language/<language>')
    def set_language(language):
        if language in Config.LANGUAGES:
            session['language'] = language
        return redirect(request.referrer or url_for('dashboard.index'))

    @app.route('/search')
    @login_required
    def search():
        query_text = request.args.get('q', '').strip()
        company_id = session.get('selected_company_id')
        results = {
            'contacts': [],
            'documents': [],
            'inventory_items': [],
            'purchase_orders': [],
            'companies': []
        }

        if query_text:
            search_term = f"%{query_text}%"
            company_ids = [company_id] if company_id else [c.id for c in current_user.companies]

            contacts = Contact.query.filter(Contact.company_id.in_(company_ids)).filter(
                or_(
                    Contact.name.ilike(search_term),
                    Contact.email.ilike(search_term),
                    Contact.identifier.ilike(search_term),
                    Contact.phone.ilike(search_term)
                )
            ).order_by(Contact.name).limit(10).all()

            results['contacts'] = [
                {
                    'title': c.name,
                    'subtitle': f"{c.type.name.title()} · {c.email or c.phone or c.identifier or ''}".strip(' · '),
                    'url': url_for('contacts.view', company_id=c.company_id, contact_id=c.id)
                }
                for c in contacts
            ]

            documents = Document.query.filter(Document.company_id.in_(company_ids)).filter(
                or_(
                    Document.document_number.ilike(search_term),
                    Document.status.ilike(search_term)
                )
            ).order_by(Document.issued_date.desc()).limit(10).all()

            results['documents'] = [
                {
                    'title': f"{d.document_number}",
                    'subtitle': f"{d.type.name.title()} · {d.status.name.title()} · {d.client.name if d.client else ''}".strip(' · '),
                    'url': url_for('invoices.view', company_id=d.company_id, id=d.id)
                }
                for d in documents
            ]

            inventory_items = InventoryItem.query.filter(InventoryItem.company_id.in_(company_ids)).filter(
                or_(
                    InventoryItem.name.ilike(search_term),
                    InventoryItem.description.ilike(search_term)
                )
            ).order_by(InventoryItem.name).limit(10).all()

            results['inventory_items'] = [
                {
                    'title': i.name,
                    'subtitle': i.description or '',
                    'url': url_for('inventory.view', company_id=i.company_id, id=i.id)
                }
                for i in inventory_items
            ]

            purchase_orders = PurchaseOrder.query.filter(PurchaseOrder.company_id.in_(company_ids)).filter(
                PurchaseOrder.order_number.ilike(search_term)
            ).order_by(PurchaseOrder.buy_date.desc()).limit(10).all()

            results['purchase_orders'] = [
                {
                    'title': p.order_number,
                    'subtitle': f"{p.supplier.name if p.supplier else ''} · {p.buy_date.isoformat() if p.buy_date else ''}".strip(' · '),
                    'url': url_for('orders.view', company_id=p.company_id, id=p.id)
                }
                for p in purchase_orders
            ]

            if not company_id:
                company_ids = [c.id for c in current_user.companies]
                company_results = Company.query.filter(Company.id.in_(company_ids)).filter(
                    or_(
                        Company.name.ilike(search_term),
                        Company.identifier.ilike(search_term),
                        Company.email.ilike(search_term),
                        Company.phone.ilike(search_term)
                    )
                ).order_by(Company.name).limit(10).all()

                results['companies'] = [
                    {
                        'title': c.name,
                        'subtitle': f"{c.identifier or ''} · {c.email or ''}".strip(' · '),
                        'url': url_for('companies.view', id=c.id)
                    }
                    for c in company_results
                ]

        return render_template('search/results.html', query=query_text, results=results)
