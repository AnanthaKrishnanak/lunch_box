"""unique reservation user date

Revision ID: c8f2a1b4d5e6
Revises: be0c6c1c9e1f
Create Date: 2026-07-22 15:32:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8f2a1b4d5e6"
down_revision: str | Sequence[str] | None = "be0c6c1c9e1f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keep the best row per (user, date): CONFIRMED > PENDING > CANCELLED,
    # then earliest created_at, then lowest id.
    op.execute(
        """
        DELETE FROM reservations
        WHERE id IN (
            SELECT id
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY slack_user_id, reservation_date
                        ORDER BY
                            CASE status
                                WHEN 'CONFIRMED' THEN 1
                                WHEN 'PENDING' THEN 2
                                WHEN 'CANCELLED' THEN 3
                                ELSE 4
                            END,
                            created_at ASC,
                            id ASC
                    ) AS rn
                FROM reservations
            ) ranked
            WHERE rn > 1
        )
        """
    )
    op.create_unique_constraint(
        "uq_reservation_user_date",
        "reservations",
        ["slack_user_id", "reservation_date"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_reservation_user_date",
        "reservations",
        type_="unique",
    )
