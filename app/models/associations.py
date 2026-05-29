from .base import db

                                             
role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True, index=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True, index=True)
)

                                           
user_companies = db.Table(
    'user_companies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True, index=True),
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id'), primary_key=True, index=True)
)

expense_tags = db.Table(
    'expense_tags',
    db.Column('expense_id', db.Integer, db.ForeignKey('expenses.id', ondelete="CASCADE"), primary_key=True, index=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True, index=True)
)

ledger_entry_tags = db.Table(
    'ledger_entry_tags',
    db.Column('ledger_entry_id', db.Integer, db.ForeignKey('ledger_entries.id', ondelete="CASCADE"), primary_key=True, index=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True, index=True)
)
