# Migration script to add the `total_credits` column to the `student` table
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = 'add_total_credits_to_student'
down_revision = '8d9ead64c41c_update_enrollment_id_to_auto_'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('student', sa.Column('total_credits', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('student', 'total_credits')