"""notebook table

Revision ID: 1ab7cfdf84d1
Revises: 55181eb651e0
Create Date: 2019-11-22 23:40:03.785065

"""
from alembic import op
import sqlalchemy as sa

from app.models import JSONEncodedObj

# revision identifiers, used by Alembic.
revision = "1ab7cfdf84d1"
down_revision = "55181eb651e0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "jupyter_notebook",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("path", sa.String(length=1024), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("parameters", JSONEncodedObj(length=1024), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_jupyter_notebook_name"), "jupyter_notebook", ["name"], unique=True
    )
    op.create_index(
        op.f("ix_jupyter_notebook_timestamp"),
        "jupyter_notebook",
        ["timestamp"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_jupyter_notebook_timestamp"), table_name="jupyter_notebook")
    op.drop_index(op.f("ix_jupyter_notebook_name"), table_name="jupyter_notebook")
    op.drop_table("jupyter_notebook")
    # ### end Alembic commands ###
