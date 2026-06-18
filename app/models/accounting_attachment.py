"""
Polymorphic attachment table shared by all accounting entry types.

reference_type: 'Expense' | 'Income' | 'Journal'
reference_id:   PK of the related record
"""
import os
from .base import db, BaseModel
from datetime import datetime, UTC


class AccountingAttachment(BaseModel):
    __tablename__ = 'accounting_attachments'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)

    # Polymorphic reference – mirrors the pattern used in LedgerEntry
    reference_type = db.Column(db.String(50), nullable=False, index=True)   # 'Expense' | 'Income' | 'Journal'
    reference_id   = db.Column(db.Integer, nullable=False, index=True)

    # Human-readable original filename (shown in UI)
    filename  = db.Column(db.String(255), nullable=False)

    # Relative path stored inside static/uploads/ (served via url_for('static', ...))
    # e.g. "uploads/receipts/abc123.pdf"
    file_path = db.Column(db.String(512), nullable=False)

    file_size  = db.Column(db.Integer, default=0)       # bytes
    mime_type  = db.Column(db.String(100), default='')

    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    # Relationships
    company       = db.relationship('Company', backref=db.backref('accounting_attachments', lazy='dynamic'))
    uploaded_by_user = db.relationship('User', foreign_keys=[uploaded_by], lazy='select')

    # ── Helpers ─────────────────────────────────────────────────────────────

    @property
    def extension(self) -> str:
        """Lowercase file extension without leading dot (e.g. 'pdf', 'jpg')."""
        return self.filename.rsplit('.', 1)[-1].lower() if '.' in self.filename else ''

    @property
    def is_image(self) -> bool:
        return self.extension in {'png', 'jpg', 'jpeg', 'webp', 'gif', 'heic'}

    @property
    def size_display(self) -> str:
        """Human-readable file size."""
        size = self.file_size or 0
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        return f'{size / (1024 * 1024):.1f} MB'

    def __repr__(self) -> str:
        return f'<AccountingAttachment {self.id} {self.reference_type}#{self.reference_id} {self.filename}>'
