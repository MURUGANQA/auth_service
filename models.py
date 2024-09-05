from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    personal = db.Column(db.Boolean, default=False)
    settings = db.Column(db.JSON, default={})
    created_at = db.Column(db.BigInteger)
    updated_at = db.Column(db.BigInteger)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile = db.Column(db.JSON, default={})
    status = db.Column(db.Integer, default=0, nullable=False)
    settings = db.Column(db.JSON, default={})
    created_at = db.Column(db.BigInteger)
    updated_at = db.Column(db.BigInteger)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    settings = db.Column(db.JSON, default={})
    created_at = db.Column(db.BigInteger)
    updated_at = db.Column(db.BigInteger)

# Schemas
class OrganizationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Organization

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role

class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member