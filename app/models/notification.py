from .base import db, BaseModel

class Notification(BaseModel):
    __tablename__ = 'notifications'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    type = db.Column(db.String(100), index=True)
    message = db.Column(db.String(1024))
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), index=True)
    
    def __repr__(self) -> str:
        return f'<Notification {self.id} {self.type}({self.status})>'                          
