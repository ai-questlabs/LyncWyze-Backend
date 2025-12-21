import uuid
from datetime import date, datetime, time

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
    phone = db.Column(db.String(32))
    # Use double precision for coordinates to avoid precision loss.
    latitude = db.Column(db.Float(precision=53))
    longitude = db.Column(db.Float(precision=53))
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
    activity_enrollments = db.relationship(
        "KidActivityEnrollment", backref="kid", cascade="all, delete-orphan", lazy=True
    )


class Vehicle(db.Model, TimestampMixin):
    __tablename__ = "vehicles"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    household_id = db.Column(db.String(36), db.ForeignKey("households.id"))
    make = db.Column(db.String(120))
    model = db.Column(db.String(120))
    color = db.Column(db.String(64))
    seat_count = db.Column(db.Integer)


class Activity(db.Model, TimestampMixin):
    __tablename__ = "activities"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    household_id = db.Column(db.String(36), db.ForeignKey("households.id"), nullable=False)
    created_by_user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    provider = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    location = db.Column(db.Text)
    latitude = db.Column(db.Float(precision=53))
    longitude = db.Column(db.Float(precision=53))

    schedule = db.relationship(
        "ActivitySchedule", backref="activity", uselist=False, cascade="all, delete-orphan"
    )
    enrollments = db.relationship(
        "KidActivityEnrollment", backref="activity", cascade="all, delete-orphan", lazy=True
    )


class KidActivityEnrollment(db.Model, TimestampMixin):
    __tablename__ = "kid_activity_enrollments"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    kid_id = db.Column(db.String(36), db.ForeignKey("kids.id"), nullable=False)
    activity_id = db.Column(db.String(36), db.ForeignKey("activities.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint("kid_id", "activity_id", name="uq_kid_activity"),)


class ActivitySchedule(db.Model, TimestampMixin):
    __tablename__ = "activity_schedules"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    activity_id = db.Column(db.String(36), db.ForeignKey("activities.id"), nullable=False, unique=True)
    schedule_type = db.Column(db.String(16), nullable=False)  # one_time | recurring
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    timezone = db.Column(db.String(64), nullable=False)
    default_start_time = db.Column(db.Time)
    default_end_time = db.Column(db.Time)
    recurrence_weekdays = db.Column(db.JSON)  # list of integers 0 (Mon) - 6 (Sun)

    day_times = db.relationship(
        "ActivityDayTime",
        backref="schedule",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="ActivityDayTime.weekday",
    )


class ActivityDayTime(db.Model, TimestampMixin):
    __tablename__ = "activity_day_times"

    id = db.Column(db.String(36), primary_key=True, default=default_uuid)
    schedule_id = db.Column(db.String(36), db.ForeignKey("activity_schedules.id"), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Monday .. 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    __table_args__ = (db.UniqueConstraint("schedule_id", "weekday", name="uq_schedule_weekday"),)
