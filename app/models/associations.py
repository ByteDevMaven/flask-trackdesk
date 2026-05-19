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
