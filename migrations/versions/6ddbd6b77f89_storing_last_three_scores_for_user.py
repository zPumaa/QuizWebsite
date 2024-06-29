"""storing last three scores for user

Revision ID: 6ddbd6b77f89
Revises: befa90e95531
Create Date: 2024-03-13 22:08:23.120987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ddbd6b77f89'
down_revision = 'befa90e95531'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('score', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_three_scores', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('score', schema=None) as batch_op:
        batch_op.drop_column('last_three_scores')

    # ### end Alembic commands ###
