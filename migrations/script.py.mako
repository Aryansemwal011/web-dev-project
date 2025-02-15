"""Add user_id to Todo

Revision ID: 14ccc7c698f3
Revises: 
Create Date: 2023-08-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14ccc7c698f3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(batch_op.f('fk_todo_user_id_user'), 'user', ['user_id'], ['id'])


def downgrade():
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_todo_user_id_user'), type_='foreignkey')
        batch_op.drop_column('user_id')
