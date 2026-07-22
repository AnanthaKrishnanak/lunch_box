"""index reservations date status created_at

Revision ID: d9e3b2c5f6a7
Revises: c8f2a1b4d5e6
Create Date: 2026-07-22 16:40:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d9e3b2c5f6a7"
down_revision: str | Sequence[str] | None = "c8f2a1b4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_reservations_date_status_created_at",
        "reservations",
        ["reservation_date", "status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_reservations_date_status_created_at",
        table_name="reservations",
    )
