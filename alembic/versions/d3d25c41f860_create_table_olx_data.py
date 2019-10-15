"""create table olx data

Revision ID: d3d25c41f860
Revises: 
Create Date: 2019-08-06 19:46:27.921956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3d25c41f860'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'bike_offers_olx',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.Text),
        sa.Column('price',  sa.Float),
        sa.Column('url_addres', sa.Text),
        sa.Column('add_time', sa.DateTime),
        sa.Column('place', sa.Text),
        sa.Column('paid_offer', sa.Boolean),
    )


def downgrade():
    op.drop_table('bike_offers_olx')
