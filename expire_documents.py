import sys

# 1. Add project directory to Python path
# REPLACE this with your actual project path on PythonAnywhere
project_home = '/home/bytecore/flask-trackdesk'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2. Import your app and initialize it
from app import create_app
from app.models import Document, Notification, db
from app.models.enums import DocumentStatus, DocumentType
from datetime import datetime, UTC

app = create_app()


def _invoice_link(document):
    return f'/{document.company_id}/invoices/{document.id}'


def _notification_exists(document, link_url):
    return Notification.query.filter(
        Notification.user_id == document.user_id,
        Notification.company_id == document.company_id,
        Notification.type == 'invoice_overdue',
        Notification.link_url == link_url,
    ).first() is not None


def _create_expired_invoice_notification(document, now):
    if document.type != DocumentType.invoice or not document.user_id:
        return False

    link_url = _invoice_link(document)
    if _notification_exists(document, link_url):
        return False

    invoice_number = document.document_number or f'#{document.id}'
    due_date = document.due_date.strftime('%d/%m/%Y') if document.due_date else 'sin fecha'
    balance_due = document.calculate_balance_due()
    body = (
        f'La factura {invoice_number} vencio el {due_date}. '
        f'Saldo pendiente: {balance_due:,.2f}.'
    )

    db.session.add(Notification(
        user_id=document.user_id,
        company_id=document.company_id,
        type='warning',
        title=f'Factura vencida {invoice_number}',
        message=body,
        body=body,
        link_url=link_url,
        priority='high',
        channel='in_app',
        status='unread',
        is_popup=True,
        sent_at=now,
    ))
    return True


# 3. Run the update logic within the app context
def run_task():
    with app.app_context():
        now = datetime.now(UTC)
        
        eligible_statuses = [
            DocumentStatus.draft,
            DocumentStatus.sent,
            DocumentStatus.issued,
            DocumentStatus.partial,
            DocumentStatus.pending
        ]
        
        expired_docs = Document.query.filter(
            Document.due_date < now,
            Document.status.in_(eligible_statuses)
        ).all()
        
        count = 0
        notification_count = 0
        for doc in expired_docs:
            notification_count += 1 if _create_expired_invoice_notification(doc, now) else 0
            doc.status = DocumentStatus.overdue
            count += 1
            
        db.session.commit()
        print(f'[OK] Updated {count} expired document(s) to overdue status.')
        print(f'[OK] Created {notification_count} expired invoice notification(s).')

if __name__ == '__main__':
    run_task()
