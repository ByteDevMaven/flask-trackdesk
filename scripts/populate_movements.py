import sys
import os
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, StockMovement, StockMovementType, PurchaseOrderItem, PurchaseOrder, DocumentItem, Document, DocumentType

def populate_movements():
    app = create_app()
    with app.app_context():
        print("Populating historical stock movements...")
        
        # 1. Process Purchase Orders (Ins)
        purchase_items = db.session.query(PurchaseOrderItem, PurchaseOrder).join(PurchaseOrder).all()
        count_in = 0
        for item, po in purchase_items:
            # Check if movement already exists to avoid duplicates if rerun
            existing = StockMovement.query.filter_by(
                inventory_item_id=item.inventory_item_id,
                reference=f"PO {po.order_number}",
                type=StockMovementType.incoming
            ).first()
            
            if not existing:
                movement = StockMovement(
                    company_id=po.company_id,
                    inventory_item_id=item.inventory_item_id,
                    type=StockMovementType.incoming,
                    quantity=item.quantity,
                    reference=f"PO {po.order_number}",
                    date=po.created_at,
                    user_id=None # POs don't have a user_id explicitly recorded in the model
                )
                db.session.add(movement)
                count_in += 1
        
        # 2. Process Invoices (Outs)
        invoice_items = db.session.query(DocumentItem, Document).join(Document)\
            .filter(Document.type == DocumentType.invoice).all()
        count_out = 0
        for item, doc in invoice_items:
            # Check if movement already exists
            existing = StockMovement.query.filter_by(
                inventory_item_id=item.inventory_item_id,
                reference=f"INV {doc.document_number}",
                type=StockMovementType.outgoing
            ).first()
            
            if not existing:
                movement = StockMovement(
                    company_id=doc.company_id,
                    inventory_item_id=item.inventory_item_id,
                    type=StockMovementType.outgoing,
                    quantity=-item.quantity, # Store as negative for outs
                    reference=f"INV {doc.document_number}",
                    date=doc.issued_date or doc.created_at,
                    user_id=doc.user_id
                )
                db.session.add(movement)
                count_out += 1
        
        db.session.commit()
        print(f"Added {count_in} incoming movements and {count_out} outgoing movements.")

if __name__ == "__main__":
    populate_movements()
