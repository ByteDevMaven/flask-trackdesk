from flask_babel import _
from app.models import db, Warehouse

class WarehouseService:
    @staticmethod
    def get_paginated_warehouses(company_id, page, per_page, search):
        query = Warehouse.query.filter_by(company_id=company_id)
        if search:
            query = query.filter(Warehouse.name.ilike(f'%{search}%') | Warehouse.location.ilike(f'%{search}%'))
            
        return query.order_by(Warehouse.id.asc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_warehouse(company_id, warehouse_id):
        return Warehouse.query.filter_by(id=warehouse_id, company_id=company_id).first_or_404()

    @staticmethod
    def create_warehouse(company_id, data):
        name = data.get('name')
        location = data.get('location', '')
        is_active = data.get('is_active') == 'on'
        
        if not name:
            raise ValueError(_('El nombre del almacén es obligatorio'))
            
        exists = Warehouse.query.filter_by(company_id=company_id, name=name).first()
        if exists:
            raise ValueError(_('Ya existe un almacén con este nombre'))
            
        warehouse = Warehouse(
            company_id=company_id,
            name=name,
            location=location,
            is_active=is_active
        )
        
        db.session.add(warehouse)
        db.session.commit()
        return warehouse

    @staticmethod
    def update_warehouse(company_id, warehouse_id, data):
        warehouse = WarehouseService.get_warehouse(company_id, warehouse_id)
        
        name = data.get('name')
        location = data.get('location', '')
        is_active = data.get('is_active') == 'on'
        
        if not name:
            raise ValueError(_('El nombre del almacén es obligatorio'))
            
        exists = Warehouse.query.filter(Warehouse.company_id == company_id, Warehouse.name == name, Warehouse.id != warehouse_id).first()
        if exists:
            raise ValueError(_('Ya existe otro almacén con este nombre'))
            
        warehouse.name = name
        warehouse.location = location
        warehouse.is_active = is_active
        
        db.session.commit()
        return warehouse
