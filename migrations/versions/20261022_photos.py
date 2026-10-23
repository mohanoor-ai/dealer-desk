"""Portable persistent photo gallery."""
from alembic import op
import sqlalchemy as sa

revision = '20261022_photos'
down_revision = '20261022_accounts'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('vehicle_photos',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('vehicle_id',sa.Integer(),sa.ForeignKey('vehicles_v2.id'),nullable=False),
        sa.Column('caption',sa.String(160),nullable=False),
        sa.Column('credit',sa.String(200),nullable=False),
        sa.Column('source_url',sa.String(1000),nullable=False),
        sa.Column('license',sa.String(100),nullable=False),
        sa.Column('license_url',sa.String(1000),nullable=False),
        sa.Column('illustrative',sa.Boolean(),nullable=False),
        sa.Column('is_cover',sa.Boolean(),nullable=False),
        sa.Column('width',sa.Integer(),nullable=False),
        sa.Column('height',sa.Integer(),nullable=False),
        sa.Column('content',sa.LargeBinary(),nullable=False),
        sa.Column('thumbnail',sa.LargeBinary(),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_vehicle_photos_vehicle_id','vehicle_photos',['vehicle_id'])

def downgrade():
    op.drop_table('vehicle_photos')
