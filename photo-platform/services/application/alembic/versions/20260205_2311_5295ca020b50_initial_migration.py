"""Initial migration

Revision ID: 5295ca020b50
Revises: 
Create Date: 2026-02-05 23:11:33.200780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5295ca020b50'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create submissions table
    op.create_table(
        'submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('gender', sa.String(length=50), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('photo_filename', sa.String(length=500), nullable=False),
        sa.Column('photo_path', sa.String(length=1000), nullable=False),
        sa.Column('photo_size', sa.Integer(), nullable=False),
        sa.Column('photo_mime_type', sa.String(length=100), nullable=False),
        sa.Column('classification_status', sa.String(length=50), nullable=False),
        sa.Column('classification_results', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('classification_error', sa.Text(), nullable=True),
        sa.Column('classified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_id'), 'submissions', ['id'], unique=False)
    op.create_index(op.f('ix_submissions_user_id'), 'submissions', ['user_id'], unique=False)
    op.create_index(op.f('ix_submissions_classification_status'), 'submissions', ['classification_status'], unique=False)
    op.create_index(op.f('ix_submissions_created_at'), 'submissions', ['created_at'], unique=False)
    op.create_index(op.f('ix_submissions_is_deleted'), 'submissions', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_submissions_photo_path'), 'submissions', ['photo_path'], unique=True)


def downgrade() -> None:
    # Drop submissions table
    op.drop_index(op.f('ix_submissions_photo_path'), table_name='submissions')
    op.drop_index(op.f('ix_submissions_is_deleted'), table_name='submissions')
    op.drop_index(op.f('ix_submissions_created_at'), table_name='submissions')
    op.drop_index(op.f('ix_submissions_classification_status'), table_name='submissions')
    op.drop_index(op.f('ix_submissions_user_id'), table_name='submissions')
    op.drop_index(op.f('ix_submissions_id'), table_name='submissions')
    op.drop_table('submissions')
