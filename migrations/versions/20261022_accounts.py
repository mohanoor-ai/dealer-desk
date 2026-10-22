"""Individual accounts and revocable sessions."""
from alembic import op
import sqlalchemy as sa

revision = '20261022_accounts'
down_revision = 'c738f767d239'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(80), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(256), nullable=False),
        sa.Column('role', sa.String(12), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.CheckConstraint("role IN ('viewer','sales','manager')"))
    op.create_table('login_sessions',
        sa.Column('token_hash', sa.String(64), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_login_sessions_user_id', 'login_sessions', ['user_id'])
    with op.batch_alter_table('audit_events_v2') as batch:
        batch.add_column(sa.Column('actor_id', sa.Integer(), nullable=True))
        batch.create_foreign_key('fk_audit_actor', 'users', ['actor_id'], ['id'])

def downgrade():
    with op.batch_alter_table('audit_events_v2') as batch:
        batch.drop_constraint('fk_audit_actor', type_='foreignkey')
        batch.drop_column('actor_id')
    op.drop_table('login_sessions')
    op.drop_table('users')
