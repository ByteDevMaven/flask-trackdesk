from .base import db, BaseModel

class Notification(BaseModel):
    __tablename__ = 'notifications'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    type = db.Column(db.String, index=True)                         
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String, index=True)                          
