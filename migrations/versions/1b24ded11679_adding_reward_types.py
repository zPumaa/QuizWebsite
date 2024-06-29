"""Adding reward types

Revision ID: 1b24ded11679
Revises: 40ff732ae5cf
Create Date: 2024-02-16 20:09:03.777579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b24ded11679'
down_revision = '40ff732ae5cf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('selected_reward_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_user_selected_reward', 'reward', ['selected_reward_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('selected_reward_id')

    with op.batch_alter_table('reward', schema=None) as batch_op:
        batch_op.drop_column('type')

    # ### end Alembic commands ###
