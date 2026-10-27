"""Historical enquiry choices and separate current email preference ledger."""
from alembic import op
import sqlalchemy as sa
revision='20261027_leads'
down_revision='20261026_customer_accounts'
branch_labels=None
depends_on=None
def upgrade():
    op.add_column('enquiries_v2',sa.Column('promotions_opt_in',sa.Boolean(),nullable=False,server_default=sa.false()))
    op.create_table('marketing_preferences',sa.Column('email',sa.String(254),primary_key=True),
        sa.Column('opted_in',sa.Boolean(),nullable=False),sa.Column('consent_at',sa.DateTime(timezone=True),nullable=True),
        sa.Column('withdrawn_at',sa.DateTime(timezone=True),nullable=True),sa.Column('history',sa.JSON(),nullable=False))
def downgrade():
    raise RuntimeError('Restore a verified backup to reverse saved consent history.')
