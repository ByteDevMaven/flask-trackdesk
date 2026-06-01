import unittest
from flask import Flask
from app import create_app
from app.models import db, Company, Warehouse
from app.warehouses.services import WarehouseService

class WarehouseServiceTestCase(unittest.TestCase):
    def setUp(self):
        # Create an app instance with testing config
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.request_context = self.app.test_request_context()
        self.request_context.push()
        
        db.create_all()
        
        # Create a test company
        self.company = Company(name='Test Company', identifier='TEST01')
        db.session.add(self.company)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.request_context.pop()
        self.app_context.pop()
        
    def test_create_warehouse_success(self):
        data = {
            'name': 'Almacén Principal',
            'location': 'Av. Central 123',
            'is_active': 'on'
        }
        warehouse = WarehouseService.create_warehouse(self.company.id, data)
        self.assertIsNotNone(warehouse.id)
        self.assertEqual(warehouse.name, 'Almacén Principal')
        self.assertEqual(warehouse.location, 'Av. Central 123')
        self.assertTrue(warehouse.is_active)
        
    def test_create_warehouse_missing_name(self):
        data = {
            'name': '',
            'location': 'Av. Central 123',
        }
        with self.assertRaises(ValueError) as context:
            WarehouseService.create_warehouse(self.company.id, data)
            
        self.assertEqual(str(context.exception), 'El nombre del almacén es obligatorio')
        
    def test_create_warehouse_duplicate_name(self):
        data = {
            'name': 'Almacén Único'
        }
        WarehouseService.create_warehouse(self.company.id, data)
        
        with self.assertRaises(ValueError) as context:
            WarehouseService.create_warehouse(self.company.id, data)
            
        self.assertEqual(str(context.exception), 'Ya existe un almacén con este nombre')

    def test_get_warehouse(self):
        data = {
            'name': 'Almacén Norte'
        }
        warehouse = WarehouseService.create_warehouse(self.company.id, data)
        
        fetched = WarehouseService.get_warehouse(self.company.id, warehouse.id)
        self.assertEqual(fetched.name, 'Almacén Norte')
        
    def test_update_warehouse_success(self):
        data = {'name': 'Almacén Viejo'}
        warehouse = WarehouseService.create_warehouse(self.company.id, data)
        
        update_data = {
            'name': 'Almacén Nuevo',
            'location': 'Calle 8',
            'is_active': '' # not 'on', so False
        }
        updated = WarehouseService.update_warehouse(self.company.id, warehouse.id, update_data)
        
        self.assertEqual(updated.name, 'Almacén Nuevo')
        self.assertEqual(updated.location, 'Calle 8')
        self.assertFalse(updated.is_active)

    def test_update_warehouse_duplicate_name(self):
        WarehouseService.create_warehouse(self.company.id, {'name': 'Almacén A'})
        warehouse_b = WarehouseService.create_warehouse(self.company.id, {'name': 'Almacén B'})
        
        update_data = {'name': 'Almacén A'}
        with self.assertRaises(ValueError) as context:
            WarehouseService.update_warehouse(self.company.id, warehouse_b.id, update_data)
            
        self.assertEqual(str(context.exception), 'Ya existe otro almacén con este nombre')

    def test_get_paginated_warehouses(self):
        WarehouseService.create_warehouse(self.company.id, {'name': 'Almacén 1'})
        WarehouseService.create_warehouse(self.company.id, {'name': 'Almacén 2'})
        WarehouseService.create_warehouse(self.company.id, {'name': 'Depósito 1'})
        
        # Test basic pagination
        paginated = WarehouseService.get_paginated_warehouses(self.company.id, 1, 10, '')
        self.assertEqual(len(paginated.items), 3)
        
        # Test search
        search_paginated = WarehouseService.get_paginated_warehouses(self.company.id, 1, 10, 'Almacén')
        self.assertEqual(len(search_paginated.items), 2)

if __name__ == '__main__':
    unittest.main()
