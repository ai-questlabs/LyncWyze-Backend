import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def default_uuid() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Household(db.Model, TimestampMixin):
    __tablename__ = "households"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    location = db.Column(db.String(255))
    avatar_url = db.Column(db.Text)

    users = db.relationship("User", backref="household", lazy=True)
    kids = db.relationship("Kid", backref="household", lazy=True)
    vehicles = db.relationship("Vehicle", backref="household", lazy=True)


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    household_id = db.Column(db.String(36), db.ForeignKey("households.id"))
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    phone = db.Column(db.String(32))
    avatar_url = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)

    kids = db.relationship("Kid", backref="parent", lazy=True, foreign_keys="Kid.parent_user_id")


class Kid(db.Model, TimestampMixin):
    __tablename__ = "kids"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    household_id = db.Column(db.String(36), db.ForeignKey("households.id"))
    parent_user_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    first_name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(32))
    avatar_url = db.Column(db.Text)


class Vehicle(db.Model, TimestampMixin):
    __tablename__ = "vehicles"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    household_id = db.Column(db.String(36), db.ForeignKey("households.id"))
    make = db.Column(db.String(120))
    model = db.Column(db.String(120))
    color = db.Column(db.String(64))
    seat_count = db.Column(db.Integer)
