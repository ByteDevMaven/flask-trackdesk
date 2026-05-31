from app import create_app
from app.middleware.rbac import ROUTE_PERMISSIONS, PUBLIC_ENDPOINTS

app = create_app()

with app.app_context():
    all_endpoints = set(rule.endpoint for rule in app.url_map.iter_rules())
    
    missing = []
    for endpoint in all_endpoints:
        if endpoint not in ROUTE_PERMISSIONS and endpoint not in PUBLIC_ENDPOINTS:
            missing.append(endpoint)
            
    print("Missing Endpoints:")
    for ep in sorted(missing):
        print(f"  - {ep}")
