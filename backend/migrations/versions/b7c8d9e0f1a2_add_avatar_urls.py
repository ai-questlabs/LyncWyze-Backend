"""Add avatar urls

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-12-18 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b7c8d9e0f1a2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("kids", sa.Column("avatar_url", sa.Text(), nullable=True))

    # Use batch mode for SQLite compatibility (ALTER COLUMN type is limited there).
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "avatar_url",
            existing_type=sa.String(length=255),
            type_=sa.Text(),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "avatar_url",
            existing_type=sa.Text(),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

    op.drop_column("kids", "avatar_url")


