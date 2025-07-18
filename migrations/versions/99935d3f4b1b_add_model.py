"""Add Model

Revision ID: 99935d3f4b1b
Revises: 27151b6a8831
Create Date: 2025-06-28 20:50:47.885600

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99935d3f4b1b'
down_revision = '27151b6a8831'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('learning_material',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('file_path', sa.String(length=200), nullable=True),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('learning_material')
    # ### end Alembic commands ###
