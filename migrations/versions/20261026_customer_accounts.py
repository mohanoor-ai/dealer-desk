"""Separate customer identities, expiring credentials and public conversations."""
from alembic import op
import sqlalchemy as sa

revision='20261026_customer_accounts'
down_revision='20261026_enquiry_workflow'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('customer_accounts',sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('email',sa.String(254),nullable=False,unique=True),sa.Column('name',sa.String(80),nullable=False),
        sa.Column('password_hash',sa.String(256),nullable=False),sa.Column('verified',sa.Boolean(),nullable=False))
    op.create_table('customer_sessions',sa.Column('token_hash',sa.String(64),primary_key=True),
        sa.Column('customer_id',sa.Integer(),sa.ForeignKey('customer_accounts.id'),nullable=False),
        sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_customer_sessions_customer_id','customer_sessions',['customer_id'])
    op.create_table('customer_tokens',sa.Column('token_hash',sa.String(64),primary_key=True),
        sa.Column('customer_id',sa.Integer(),sa.ForeignKey('customer_accounts.id'),nullable=False),
        sa.Column('purpose',sa.String(12),nullable=False),sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False))
    with op.batch_alter_table('enquiries_v2') as batch:
        batch.add_column(sa.Column('customer_account_id',sa.Integer(),nullable=True))
        batch.create_foreign_key('fk_enquiry_customer','customer_accounts',['customer_account_id'],['id'])
        batch.create_index('ix_enquiry_customer','customer_account_id'.split())
    op.create_table('enquiry_messages',sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('enquiry_id',sa.Integer(),sa.ForeignKey('enquiries_v2.id'),nullable=False),
        sa.Column('author_role',sa.String(12),nullable=False),sa.Column('body',sa.String(2000),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_enquiry_messages_enquiry_id','enquiry_messages',['enquiry_id'])

def downgrade():
    raise RuntimeError('Restore a verified backup to reverse customer account data.')
