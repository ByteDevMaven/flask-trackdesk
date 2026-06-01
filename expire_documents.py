import sys

# 1. Add project directory to Python path
# REPLACE this with your actual project path on PythonAnywhere
project_home = '/home/bytecore/flask-trackdesk'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2. Import your app and initialize it
from app import create_app
from app.models import Document, db
from app.models.enums import DocumentStatus
from datetime import datetime, UTC

app = create_app()

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
        for doc in expired_docs:
            doc.status = DocumentStatus.overdue
            count += 1
            
        db.session.commit()
        print(f'[OK] Updated {count} expired document(s) to overdue status.')

if __name__ == '__main__':
    run_task()
