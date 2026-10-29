"""Adding visits and weekly_reports tables

Revision ID: f3a9c1d2b4e5
Revises: d53d26fba49d
Create Date: 2026-10-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a9c1d2b4e5'
down_revision: Union[str, Sequence[str], None] = 'd53d26fba49d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('visits',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('from_cv', sa.Boolean(), nullable=False),
    sa.Column('visitor_id', sa.UUID(), nullable=False),
    sa.Column('user_agent', sa.String(length=512), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_visits_created_at', 'visits', ['created_at'], unique=False)
    op.create_table('weekly_reports',
    sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('period_end')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('weekly_reports')
    op.drop_index('idx_visits_created_at', table_name='visits')
    op.drop_table('visits')
