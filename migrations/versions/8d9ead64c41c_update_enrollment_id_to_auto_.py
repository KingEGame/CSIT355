"""Update enrollment_id to auto-incrementing integer

Revision ID: 8d9ead64c41c
Revises: 35e824538476
Create Date: 2025-05-01 16:21:12.856171

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8d9ead64c41c'
down_revision = '35e824538476'
branch_labels = None
depends_on = None


def upgrade():
    # Temporarily drop the primary key constraint
    with op.batch_alter_table('enrolled', schema=None) as batch_op:
        batch_op.drop_constraint('PRIMARY', type_='primary')

    # Migrate existing data to integers
    op.execute("SET @row_number = 0;")
    op.execute("UPDATE enrolled SET enrollment_id = (@row_number:=@row_number + 1);")

    # Alter the column to INTEGER
    with op.batch_alter_table('enrolled', schema=None) as batch_op:
        batch_op.alter_column('enrollment_id',
               existing_type=mysql.VARCHAR(length=10),
               type_=sa.Integer(),
               existing_nullable=False)

    # Reapply the primary key constraint with AUTO_INCREMENT
    op.execute("ALTER TABLE enrolled ADD PRIMARY KEY (enrollment_id);")
    op.execute("ALTER TABLE enrolled MODIFY enrollment_id INTEGER NOT NULL AUTO_INCREMENT;")

def downgrade():
    # Revert the column to VARCHAR(10)
    with op.batch_alter_table('enrolled', schema=None) as batch_op:
        batch_op.alter_column('enrollment_id',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(length=10),
               existing_nullable=False)

    # Reapply the original primary key constraint
    op.execute("ALTER TABLE enrolled ADD PRIMARY KEY (enrollment_id);")
