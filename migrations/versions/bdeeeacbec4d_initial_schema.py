"""Initial schema

Revision ID: bdeeeacbec4d
Revises:
Create Date: 2020-04-11 11:20:18.814141

"""
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bdeeeacbec4d'
down_revision = None
branch_labels = None
depends_on = None


DEFAULT_NOTIFICATIONS = {
    'innostore': 'off',
    'volunteering': 'off',
    'project_creation': 'off',
    'administration': 'off',
    'service': 'email',
}


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts',
    sa.Column('full_name', sa.String(length=256), nullable=False),
    sa.Column('group', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('telegram_username', sa.String(length=32), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('notification_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=json.dumps(DEFAULT_NOTIFICATIONS)),
    sa.PrimaryKeyConstraint('email')
    )
    op.create_table('colors',
    sa.Column('value', sa.String(length=6), nullable=False),
    sa.PrimaryKeyConstraint('value')
    )
    op.create_table('competences',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('type', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=1024), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('addition_time', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'type', name='unique product')
    )
    op.create_table('sizes',
    sa.Column('value', sa.String(length=3), nullable=False),
    sa.PrimaryKeyConstraint('value')
    )
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipient_email', sa.String(length=128), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('type', sa.Enum('purchase_status_changed', 'new_arrivals', 'claim_innopoints', 'application_status_changed', 'service', 'manual_transaction', 'project_review_status_changed', 'all_feedback_in', 'added_as_moderator', 'out_of_stock', 'new_purchase', 'project_review_requested', name='notificationtype'), nullable=False),
    sa.ForeignKeyConstraint(['recipient_email'], ['accounts.email'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('static_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mimetype', sa.String(length=255), nullable=False),
    sa.Column('owner_email', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['owner_email'], ['accounts.email'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('varieties',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('size', sa.String(length=3), nullable=True),
    sa.Column('color', sa.String(length=6), nullable=True),
    sa.ForeignKeyConstraint(['color'], ['colors.value'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['size'], ['sizes.value'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('variety_id', sa.Integer(), nullable=False),
    sa.Column('image_id', sa.Integer(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['image_id'], ['static_files.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['variety_id'], ['varieties.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('variety_id', 'order', deferrable='True', initially='DEFERRED', name='unique order indices')
    )
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.Column('creation_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('organizer', sa.String(length=128), nullable=True),
    sa.Column('creator_email', sa.String(length=128), nullable=False),
    sa.Column('admin_feedback', sa.String(length=1024), nullable=True),
    sa.Column('review_status', sa.Enum('pending', 'approved', 'rejected', name='reviewstatus'), nullable=True),
    sa.Column('lifetime_stage', sa.Enum('draft', 'ongoing', 'finalizing', 'finished', name='lifetimestage'), nullable=False),
    sa.ForeignKeyConstraint(['creator_email'], ['accounts.email'], ),
    sa.ForeignKeyConstraint(['image_id'], ['static_files.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('stock_changes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.Enum('carried_out', 'pending', 'ready_for_pickup', 'rejected', name='stockchangestatus'), nullable=False),
    sa.Column('account_email', sa.String(length=128), nullable=False),
    sa.Column('variety_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_email'], ['accounts.email'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['variety_id'], ['varieties.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=1024), nullable=True),
    sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('working_hours', sa.Integer(), nullable=False),
    sa.Column('reward_rate', sa.Integer(), nullable=False),
    sa.Column('fixed_reward', sa.Boolean(), nullable=False),
    sa.Column('people_required', sa.Integer(), nullable=False),
    sa.Column('telegram_required', sa.Boolean(), nullable=False),
    sa.Column('application_deadline', sa.DateTime(timezone=True), nullable=True),
    sa.Column('feedback_questions', sa.ARRAY(sa.String(length=1024)), nullable=False),
    sa.Column('internal', sa.Boolean(), nullable=False, server_default='False'),
    sa.CheckConstraint('(fixed_reward AND working_hours = 1) OR (NOT fixed_reward AND reward_rate = 70)', name='reward policy'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'project_id', name='name is unique inside a project')
    )
    op.create_table('project_files',
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['static_files.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('project_id', 'file_id')
    )
    op.create_table('project_moderation',
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('account_email', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['account_email'], ['accounts.email'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('project_id', 'account_email')
    )
    op.create_table('activity_competence',
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('competence_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['competence_id'], ['competences.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('activity_id', 'competence_id')
    )
    op.create_table('applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('applicant_email', sa.String(length=128), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(length=1024), nullable=True),
    sa.Column('application_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('telegram_username', sa.String(length=32), nullable=True),
    sa.Column('status', sa.Enum('approved', 'pending', 'rejected', name='applicationstatus'), nullable=False),
    sa.Column('actual_hours', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['applicant_email'], ['accounts.email'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('applicant_email', 'activity_id', name='only one application')
    )
    op.create_table('feedback',
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('answers', sa.ARRAY(sa.String(length=1024)), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('application_id'),
    sa.UniqueConstraint('application_id')
    )
    op.create_table('reports',
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('reporter_email', sa.String(length=128), nullable=False),
    sa.Column('time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=1024), nullable=True),
    sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
    sa.ForeignKeyConstraint(['reporter_email'], ['accounts.email'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('application_id', 'reporter_email')
    )
    op.create_table('feedback_competence',
    sa.Column('feedback_id', sa.Integer(), nullable=False),
    sa.Column('competence_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['competence_id'], ['competences.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['feedback_id'], ['feedback.application_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('feedback_id', 'competence_id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_email', sa.String(length=128), nullable=False),
    sa.Column('change', sa.Integer(), nullable=False),
    sa.Column('stock_change_id', sa.Integer(), nullable=True),
    sa.Column('feedback_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('(stock_change_id IS NULL) OR (feedback_id IS NULL)', name='not(feedback and stock_change)'),
    sa.ForeignKeyConstraint(['account_email'], ['accounts.email'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['feedback_id'], ['feedback.application_id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['stock_change_id'], ['stock_changes.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('feedback_competence')
    op.drop_table('reports')
    op.drop_table('feedback')
    op.drop_table('applications')
    op.drop_table('activity_competence')
    op.drop_table('project_moderation')
    op.drop_table('project_files')
    op.drop_table('activities')
    op.drop_table('stock_changes')
    op.drop_table('projects')
    op.drop_table('product_images')
    op.drop_table('varieties')
    op.drop_table('static_files')
    op.drop_table('notifications')
    op.drop_table('sizes')
    op.drop_table('products')
    op.drop_table('competences')
    op.drop_table('colors')
    op.drop_table('accounts')
    # ### end Alembic commands ###