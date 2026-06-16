
from flask import g, session, request, has_request_context
from flask_login import current_user
from sqlalchemy import event
from app.extensions import db
from app.models.audit import AuditLog
from app.models.base import BaseModel

from datetime import datetime
import decimal
import enum
import json


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        from datetime import datetime, date
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, enum.Enum):
            return obj.value
        return super(AlchemyEncoder, self).default(obj)

class AuditMiddleware:
    @staticmethod
    def log_change(target, action, old_data=None, new_data=None):
        """
        Manually log a change. Useful if automated listeners are not enough.
        """
        try:
            user_id = None
            company_id = getattr(target, 'company_id', None)
            
            if has_request_context():
                if current_user and current_user.is_authenticated:
                    user_id = current_user.id
                    
                if not company_id:
                    company_id = request.headers.get('X-Company-Id')
                        
            # Fallback for background tasks or legacy contexts
            if not user_id:
                user_id = getattr(target, 'user_id', None)

            try:
                if not user_id and session:
                    user_id = session.get('user_id')
            except Exception:
                pass
            if not user_id and hasattr(g, 'user') and g.user:
                user_id = g.user.id
                
            try:
                if not company_id and session:
                    company_id = session.get('company_id')
            except Exception:
                pass
            if not company_id and hasattr(g, 'current_company') and g.current_company:
                company_id = g.current_company.id

            def serialize_json(data):
                if not data:
                    return None
                return json.loads(json.dumps(data, cls=AlchemyEncoder))

            # Ensure record_id is Integer
            rec_id = None
            if hasattr(target, 'id') and target.id is not None:
                try:
                    rec_id = int(target.id)
                except (ValueError, TypeError):
                    pass

            audit_log = AuditLog(
                company_id=int(company_id) if company_id else None,
                user_id=int(user_id) if user_id else None,
                action=action,
                table_name=target.__tablename__,
                record_id=rec_id,
                old_data=serialize_json(old_data),
                new_data=serialize_json(new_data)
            )
            db.session.add(audit_log)
            # Do not commit here, let the main transaction handle it
        except Exception as e:
            # Avoid breaking the main transaction if logging fails
            print(f"Audit Logging Error: {str(e)}")

def get_model_changes(target):
    """Helper to detect changed attributes and their values."""
    state = db.inspect(target)
    old_data = {}
    new_data = {}
    for attr in state.mapper.column_attrs:
        hist = state.get_history(attr.key, True)
        if hist.has_changes():
            old_data[attr.key] = hist.deleted[0] if hist.deleted else None
            new_data[attr.key] = hist.added[0] if hist.added else None
    return old_data, new_data

def register_audit_listeners():
    """ Registers global SQLAlchemy listeners for all models inheriting from Base. """
    @event.listens_for(db.session, 'before_flush')
    def receive_before_flush(session, flush_context, instances):
        for obj in session.new:
            if isinstance(obj, BaseModel) and not isinstance(obj, AuditLog):
                # For new objects, we don't have an ID yet usually, 
                # but we can capture the initial data
                new_data = {c.key: getattr(obj, c.key) for c in db.inspect(obj).mapper.column_attrs}
                AuditMiddleware.log_change(obj, 'CREATE', new_data=new_data)

        for obj in session.dirty:
            if isinstance(obj, BaseModel) and not isinstance(obj, AuditLog):
                old_data, new_data = get_model_changes(obj)
                if old_data or new_data:
                    AuditMiddleware.log_change(obj, 'UPDATE', old_data=old_data, new_data=new_data)

        for obj in session.deleted:
            if isinstance(obj, BaseModel) and not isinstance(obj, AuditLog):
                old_data = {c.key: getattr(obj, c.key) for c in db.inspect(obj).mapper.column_attrs}
                AuditMiddleware.log_change(obj, 'DELETE', old_data=old_data)
