import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db, StockMovement, StockMovementType
try:
    app = create_app()
    with app.app_context():
        # Ensure table exists
        db.create_all()
        # Count movements
        count = StockMovement.query.count()
        print(f"Current StockMovement count: {count}")
except Exception as e:
    print(f"Error: {e}")
