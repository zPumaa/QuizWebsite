"""Added fifty_count to user

Revision ID: 38b908c38b41
Revises: 1b24ded11679
Create Date: 2024-02-17 22:24:42.816647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38b908c38b41'
down_revision = '1b24ded11679'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fifty_count', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('fifty_count')

    # ### end Alembic commands ###
