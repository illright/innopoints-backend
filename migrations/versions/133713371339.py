"""empty message

Revision ID: 133713371338
Revises: 563841f14d37
Create Date: 2019-12-26 21:10:14.032751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1337133713389'
down_revision = '1337133713388'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE lifetimestage RENAME TO lifetimestage_old;")
    op.execute("CREATE TYPE lifetimestage AS enum('draft', 'ongoing', 'finalizing', 'finished');")
    op.execute("ALTER TABLE projects ALTER COLUMN lifetime_stage TYPE lifetimestage USING lifetime_stage::text::lifetimestage;")
    op.execute("DROP TYPE lifetimestage_old;")



def downgrade():
    op.execute("ALTER TYPE lifetimestage RENAME TO lifetimestage_old;")
    op.execute("CREATE TYPE lifetimestage AS enum('draft', 'ongoing', 'past');")
    op.execute("ALTER TABLE projects ALTER COLUMN lifetime_stage TYPE lifetimestage USING lifetime_stage::text::lifetimestage;")
    op.execute("DROP TYPE lifetimestage_old;")
