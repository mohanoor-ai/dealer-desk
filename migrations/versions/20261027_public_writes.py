"""Shared, bounded rate budget for explicitly enabled hosted public writes."""
from alembic import op
import sqlalchemy as sa
revision='20261027_public_writes'
down_revision='20261027_leads'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('public_write_windows',sa.Column('service',sa.String(30),primary_key=True),
        sa.Column('window',sa.Integer(),nullable=False),sa.Column('count',sa.Integer(),nullable=False),
        sa.CheckConstraint('count >= 0',name='ck_public_write_count'))
def downgrade():
    op.drop_table('public_write_windows')
