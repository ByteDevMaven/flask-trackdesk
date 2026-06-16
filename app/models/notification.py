from datetime import datetime, UTC

from .base import db, BaseModel

class Notification(BaseModel):
    __tablename__ = 'notifications'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    type = db.Column(db.String(100), default='info', nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, default='Notificacion')
    message = db.Column(db.String(1024))
    body = db.Column(db.String(2048))
    link_url = db.Column(db.String(512))
    priority = db.Column(db.String(20), default='normal', nullable=False, index=True)
    channel = db.Column(db.String(50), default='in_app', nullable=False, index=True)

    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    status = db.Column(db.String(50), default='unread', nullable=False, index=True)
    is_popup = db.Column(db.Boolean, default=False, nullable=False, index=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='notifications', lazy='select')
    created_by = db.relationship('User', foreign_keys=[created_by_id], lazy='select')
    company = db.relationship('Company', backref='notifications', lazy='select')

    @property
    def display_body(self):
        return self.body or self.message or ''

    @property
    def is_unread(self):
        return self.status == 'unread' and self.read_at is None
    
    def __repr__(self) -> str:
        return f'<Notification {self.id} {self.type}({self.status})>'
