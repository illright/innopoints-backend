"""Add draft activities

Revision ID: 97b4e9faecc5
Revises: a202c9fa5b73
Create Date: 2020-06-10 14:09:31.302007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97b4e9faecc5'
down_revision = 'a202c9fa5b73'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activities', sa.Column('draft', sa.Boolean(), nullable=False, server_default='True'))
    op.drop_constraint('name is unique inside a project', 'activities', type_='unique')
    op.alter_column('projects', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    op.drop_constraint('projects_name_key', 'projects', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('projects_name_key', 'projects', ['name'])
    op.alter_column('projects', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.create_unique_constraint('name is unique inside a project', 'activities', ['name', 'project_id'])
    op.drop_column('activities', 'draft')
    # ### end Alembic commands ###
