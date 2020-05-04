"""Remove the organizer field

Revision ID: c8f1d96845f3
Revises: e2b7e2a597a5
Create Date: 2020-04-27 15:30:42.207876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8f1d96845f3'
down_revision = 'e2b7e2a597a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'feedback', ['application_id'])
    op.drop_column('projects', 'organizer')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('organizer', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'feedback', type_='unique')
    # ### end Alembic commands ###