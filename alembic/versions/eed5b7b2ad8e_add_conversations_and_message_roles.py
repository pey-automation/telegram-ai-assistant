"""add conversations and message roles

Revision ID: eed5b7b2ad8e
Revises: 6768fc62dec6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "eed5b7b2ad8e"
down_revision: Union[str, Sequence[str], None] = "6768fc62dec6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # conversations already exists in the database,
    # so only add the missing columns to messages.

    op.add_column(
        "messages",
        sa.Column(
            "conversation_id",
            sa.Integer(),
            sa.ForeignKey("conversations.id"),
            nullable=True,
        ),
    )

    op.add_column(
        "messages",
        sa.Column(
            "role",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("messages", "role")
    op.drop_column("messages", "conversation_id")