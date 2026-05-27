from datetime import datetime, UTC
from app.extensions import db
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy import event

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

from sqlalchemy.orm import Session

@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    if (
        execute_state.is_select
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                BaseModel,
                lambda cls: (cls.is_deleted == False) | (cls.is_deleted == None),
                include_aliases=True
            )
        )
