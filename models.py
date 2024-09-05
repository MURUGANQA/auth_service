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

    roles = db.relationship('Role', backref='organization', lazy=True)
    members = db.relationship('Member', backref='organization', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile = db.Column(db.JSON, default={})
    status = db.Column(db.Integer, default=0, nullable=False)
    settings = db.Column(db.JSON, default={})
    created_at = db.Column(db.BigInteger)
    updated_at = db.Column(db.BigInteger)

    members = db.relationship('Member', backref='user', lazy=True)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    members = db.relationship('Member', backref='role', lazy=True)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    settings = db.Column(db.JSON, default={})
    created_at = db.Column(db.BigInteger)
    updated_at = db.Column(db.BigInteger)
