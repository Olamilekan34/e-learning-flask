"""Add Model

Revision ID: f3c3b047d31d
Revises: f4baf8e1c43d
Create Date: 2025-03-30 12:28:23.806129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3c3b047d31d'
down_revision = 'f4baf8e1c43d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.drop_constraint('course_instructor_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'educators', ['instructor_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('course_instructor_id_fkey', 'user', ['instructor_id'], ['id'])

    # ### end Alembic commands ###
