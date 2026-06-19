import sys

# 1. Add project directory to Python path
# REPLACE this with your actual project path on PythonAnywhere
project_home = '/home/bytecore/flask-trackdesk'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2. Import your app and initialize it
from app import create_app
from app.inventory.services import send_low_stock_notifications

app = create_app()


# 3. Run the notification logic within the app context
def run_task():
    with app.app_context():
        result = send_low_stock_notifications()
        print(f"[OK] Checked {result['checked_items']} low-stock item(s).")
        print(f"[OK] Created {result['created_notifications']} low-stock notification(s).")


if __name__ == '__main__':
    run_task()
