from .base import db, BaseModel

class Notification(BaseModel):
    __tablename__ = 'notifications'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    type = db.Column(db.String, index=True)  # 'email' or 'whatsapp'
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String, index=True)  # 'sent', 'failed', etc.
