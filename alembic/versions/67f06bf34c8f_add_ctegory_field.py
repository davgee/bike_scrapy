"""Add ctegory field

Revision ID: 67f06bf34c8f
Revises: a7b295695a66
Create Date: 2020-07-29 19:09:31.516245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67f06bf34c8f'
down_revision = 'a7b295695a66'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'bike_offers_olx',
        sa.Column('category', sa.Text)
    )


def downgrade():
    op.drop_column(
        'category'
    )
