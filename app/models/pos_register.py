from datetime import datetime, UTC

from .base import db, BaseModel


class PosRegisterSession(BaseModel):
    __tablename__ = "pos_register_sessions"

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True, index=True)
    register_name = db.Column(db.String(100), nullable=False, default="Caja principal")
    status = db.Column(db.String(20), nullable=False, default="open", index=True)
    opening_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    expected_cash_amount = db.Column(db.Numeric(12, 2), nullable=True)
    closing_amount = db.Column(db.Numeric(12, 2), nullable=True)
    opened_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), index=True)
    closed_at = db.Column(db.DateTime, nullable=True, index=True)
    notes = db.Column(db.String(1024), nullable=True)
    closing_notes = db.Column(db.String(1024), nullable=True)

    company = db.relationship("Company", backref="pos_register_sessions", lazy="select")
    user = db.relationship("User", backref="pos_register_sessions", lazy="select")
    warehouse = db.relationship("Warehouse", backref="pos_register_sessions", lazy="select")
    payments = db.relationship("Payment", backref="pos_register_session", lazy="dynamic")

    __table_args__ = (
        db.CheckConstraint("opening_amount >= 0", name="check_pos_register_opening_non_negative"),
        db.CheckConstraint("closing_amount IS NULL OR closing_amount >= 0", name="check_pos_register_closing_non_negative"),
        db.CheckConstraint("status IN ('open', 'closed')", name="check_pos_register_status"),
    )

    def __repr__(self) -> str:
        return f"<PosRegisterSession {self.id} {self.register_name} ({self.status})>"


class PosCashMovement(BaseModel):
    __tablename__ = "pos_cash_movements"

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    register_session_id = db.Column(db.Integer, db.ForeignKey("pos_register_sessions.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    movement_type = db.Column(db.String(20), nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    reason = db.Column(db.String(255), nullable=False, default="")

    company = db.relationship("Company", backref="pos_cash_movements", lazy="select")
    register_session = db.relationship("PosRegisterSession", backref=db.backref("cash_movements", lazy="dynamic"))
    user = db.relationship("User", backref="pos_cash_movements", lazy="select")

    __table_args__ = (
        db.CheckConstraint("amount > 0", name="check_pos_cash_movement_amount_positive"),
        db.CheckConstraint("movement_type IN ('cash_in', 'cash_out')", name="check_pos_cash_movement_type"),
    )

    def __repr__(self) -> str:
        return f"<PosCashMovement {self.id} {self.movement_type} {self.amount}>"
