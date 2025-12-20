"""Add household coordinates and phone

Revision ID: d4e5f6g7h9i0
Revises: c3d4e5f6g7h8
Create Date: 2025-12-21 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d4e5f6g7h9i0"
down_revision = "c3d4e5f6g7h8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("households", sa.Column("phone", sa.String(length=32), nullable=True))
    # Use double precision to match the model and avoid precision loss.
    op.add_column("households", sa.Column("latitude", sa.Float(precision=53), nullable=True))
    op.add_column("households", sa.Column("longitude", sa.Float(precision=53), nullable=True))
    op.drop_column("households", "location")


def downgrade() -> None:
    op.add_column("households", sa.Column("location", sa.String(length=255), nullable=True))
    op.drop_column("households", "longitude")
    op.drop_column("households", "latitude")
    op.drop_column("households", "phone")


