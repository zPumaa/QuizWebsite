"""Added country_code to user

Revision ID: 6ab57dfc9e1c
Revises: 38b908c38b41
Create Date: 2024-02-24 20:48:19.809238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ab57dfc9e1c'
down_revision = '38b908c38b41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('country_code', sa.String(length=5), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('country_code')

    # ### end Alembic commands ###
