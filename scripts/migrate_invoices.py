import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Document, DocumentType
import argparse

def migrate_invoices(dry_run=True):
    app = create_app()
    with app.app_context():
        # Get all documents that are invoices
        invoices = Document.query.filter_by(type=DocumentType.invoice).all()
        print(f"Found {len(invoices)} total invoices in the database.")
        
        updated_count = 0
        skipped_count = 0
        
        for invoice in invoices:
            old_number = invoice.document_number
            
            # Check if it starts with 'I-' (Legacy format: I-COMPANY_ID-SEQ)
            # Example: I-100000-000001
            if old_number.startswith('I-'):
                parts = old_number.split('-')
                if len(parts) >= 3:
                     # Segment 0: 'I', Segment 1: Company ID, Segment 2: Sequence Number
                     seq_str = parts[-1] 
                     try:
                         seq_num = int(seq_str)
                         # New format: 000-001-01-XXXXXXXX
                         new_number = f"000-001-01-{seq_num:08d}"
                         
                         print(f"MIGRATING: {old_number.ljust(20)} -> {new_number}")
                         invoice.document_number = new_number
                         updated_count += 1
                     except ValueError:
                         print(f"ERROR: Could not parse sequence from '{old_number}'. Segment: '{seq_str}'. Skipping.")
                         skipped_count += 1
                else:
                    print(f"SKIP: Unexpected legacy format '{old_number}'. Expected 'I-COMPANYID-SEQ'. Skipping.")
                    skipped_count += 1
            elif old_number.startswith('000-001-01-'):
                # print(f"SKIP: '{old_number}' is already in the new SAR format.")
                skipped_count += 1
            else:
                print(f"SKIP: '{old_number}' does not match legacy prefix 'I-'. Skipping.")
                skipped_count += 1
        
        if updated_count > 0 and not dry_run:
            try:
                db.session.commit()
                print(f"\nSUCCESS: Migration committed to database.")
                print(f"Updated: {updated_count}")
                print(f"Skipped: {skipped_count}")
            except Exception as e:
                db.session.rollback()
                print(f"\nFATAL ERROR during commit: {str(e)}")
        else:
            if updated_count == 0:
                 print("\nNo records were eligible for migration.")
            else:
                 print(f"\nDRY RUN COMPLETED: No changes were committed to the database.")
                 print(f"Would update: {updated_count} records.")
                 print(f"Would skip:   {skipped_count} records.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Migrate existing invoice numbers to SAR Honduras format.')
    parser.add_argument('--commit', action='store_true', help='Actually apply changes to the database (default is dry-run)')
    args = parser.parse_args()
    
    migrate_invoices(dry_run=not args.commit)
