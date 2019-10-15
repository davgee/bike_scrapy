"""Add Description column and added via phone

Revision ID: a7b295695a66
Revises: d3d25c41f860
Create Date: 2019-08-09 19:22:53.610478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7b295695a66'
down_revision = 'd3d25c41f860'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'bike_offers_olx',
        sa.Column('description', sa.Text)
    )
    op.add_column(
        'bike_offers_olx',
        sa.Column('added_via_phone', sa.Boolean, nullable=True)
    )


def downgrade():
    op.drop_column(
        'description'
    )
    op.drop_column(
        'added_via_phone'
    )
