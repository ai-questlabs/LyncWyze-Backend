"""Add activities tables and coords

Revision ID: e1f2g3h4i5j6
Revises: d4e5f6g7h9i0
Create Date: 2025-12-21 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "e1f2g3h4i5j6"
down_revision = "d4e5f6g7h9i0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Float(precision=53), nullable=True),
        sa.Column("longitude", sa.Float(precision=53), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "activity_schedules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("activity_id", sa.String(length=36), nullable=False),
        sa.Column("schedule_type", sa.String(length=16), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("default_start_time", sa.Time(), nullable=True),
        sa.Column("default_end_time", sa.Time(), nullable=True),
        sa.Column("recurrence_weekdays", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("activity_id"),
    )

    op.create_table(
        "activity_day_times",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("schedule_id", sa.String(length=36), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["schedule_id"], ["activity_schedules.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("schedule_id", "weekday", name="uq_schedule_weekday"),
    )

    op.create_table(
        "kid_activity_enrollments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("kid_id", sa.String(length=36), nullable=False),
        sa.Column("activity_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"]),
        sa.ForeignKeyConstraint(["kid_id"], ["kids.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kid_id", "activity_id", name="uq_kid_activity"),
    )


def downgrade() -> None:
    op.drop_table("kid_activity_enrollments")
    op.drop_table("activity_day_times")
    op.drop_table("activity_schedules")
    op.drop_table("activities")


