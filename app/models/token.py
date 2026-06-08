from datetime import datetime, UTC, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.base import BaseModel

class Token(BaseModel):
    __tablename__ = 'tokens'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token_hash = Column(String(128), unique=True, nullable=False)
    type = Column(String(32), nullable=False, default='password_reset')
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    is_valid = Column(Boolean, default=True, nullable=False)

    user = relationship("User", backref=db.backref("tokens", cascade="all, delete-orphan"))

    def is_expired(self) -> bool:
        """Check if the token has expired."""
        # SQLite strips tzinfo, so compare naive UTC datetimes
        now = datetime.utcnow()
        exp = self.expires_at.replace(tzinfo=None) if self.expires_at.tzinfo else self.expires_at
        return now > exp

    def mark_used(self):
        """Mark the token as used."""
        self.used_at = datetime.now(UTC)
        self.is_valid = False
