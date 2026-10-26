"""Persist source, request, contact details and staff-confirmed workflow history."""
from alembic import op
import sqlalchemy as sa

revision = '20261026_enquiry_workflow'
down_revision = '20261022_photos'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite batch rebuild also preserves existing primary keys and child references.
    with op.batch_alter_table('enquiries_v2',table_args=(
        sa.CheckConstraint("status IN ('new','contacted','closed')",name='ck_enquiry_status'),
        sa.CheckConstraint('revision >= 1',name='ck_enquiry_revision'),
    )) as batch:
        batch.alter_column('vehicle_id', existing_type=sa.Integer(), nullable=True)
        for name, length, default in [('source',20,'Other'),('request_type',30,'Other'),
                                      ('email',254,''),('phone',40,''),('closure_reason',300,'')]:
            batch.add_column(sa.Column(name,sa.String(length),nullable=False,server_default=default))
        batch.add_column(sa.Column('activity',sa.JSON(),nullable=False,server_default='[]'))
        batch.add_column(sa.Column('submission_key',sa.String(36),nullable=True))
        batch.create_index('uq_enquiry_submission_key',['submission_key'],unique=True)


def downgrade():
    # General enquiries cannot be assigned to an invented vehicle on rollback.
    raise RuntimeError('Restore a verified backup to downgrade enquiry workflow data.')
