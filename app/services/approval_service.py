from datetime import datetime, UTC
from app.models import db, ApprovalRequest, ApprovalStatus

class ActionRegistry:
    _handlers = {}

    @classmethod
    def register(cls, name, handler):
        """Register a function to handle an approval action."""
        cls._handlers[name] = handler

    @classmethod
    def execute(cls, name, payload):
        """Execute a registered action with the given payload."""
        if name not in cls._handlers:
            raise ValueError(f"No handler registered for action: {name}")
        return cls._handlers[name](**payload)

class ApprovalService:
    @staticmethod
    def create_request(company_id, requester_id, action_type, payload):
        req = ApprovalRequest(
            company_id=company_id,
            requester_id=requester_id,
            action_type=action_type,
            payload=payload,
            status=ApprovalStatus.pending
        )
        db.session.add(req)
        db.session.commit()
        return req

    @staticmethod
    def approve_request(request_id, approver_id):
        req = ApprovalRequest.query.get_or_404(request_id)
        if req.status != ApprovalStatus.pending:
            raise ValueError("Request is not pending")
        
        # Execute the action
        ActionRegistry.execute(req.action_type, req.payload)
        
        req.status = ApprovalStatus.approved
        req.approver_id = approver_id
        req.resolved_at = datetime.now(UTC)
        db.session.commit()
        return req

    @staticmethod
    def reject_request(request_id, approver_id):
        req = ApprovalRequest.query.get_or_404(request_id)
        if req.status != ApprovalStatus.pending:
            raise ValueError("Request is not pending")
        
        req.status = ApprovalStatus.rejected
        req.approver_id = approver_id
        req.resolved_at = datetime.now(UTC)
        db.session.commit()
        return req

    @staticmethod
    def get_pending_requests(company_id):
        return ApprovalRequest.query.filter_by(
            company_id=company_id, 
            status=ApprovalStatus.pending
        ).order_by(ApprovalRequest.created_at.desc()).all()

    @staticmethod
    def get_resolved_requests(company_id, limit=50):
        return ApprovalRequest.query.filter(
            ApprovalRequest.company_id == company_id,
            ApprovalRequest.status != ApprovalStatus.pending
        ).order_by(ApprovalRequest.resolved_at.desc()).limit(limit).all()

def init_action_handlers():
    from app.inventory.services.inventory_service import InventoryService
    
    # We map the kwargs from the ApprovalRequest payload directly to the service method
    ActionRegistry.register('adjust_stock', InventoryService.adjust_stock)

