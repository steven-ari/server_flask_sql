"""Initial migration.

Revision ID: 3de61b57a245
Revises: 
Create Date: 2023-07-29 18:53:21.371557

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3de61b57a245'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pdfs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('pdf_path', sa.Text(), nullable=False),
    sa.Column('pdf_filename', sa.String(length=255), nullable=False),
    sa.Column('ocr_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('accepted_tos', sa.Boolean(), nullable=True),
    sa.Column('date_accepted_tos', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('categories',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('icon_path', sa.Text(), nullable=True),
    sa.Column('color_code', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('docu_user',
    sa.Column('docu_id', sa.BigInteger(), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['docu_id'], ['pdfs.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table('images',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('pdf_id', sa.BigInteger(), nullable=False),
    sa.Column('image_path', sa.Text(), nullable=False),
    sa.Column('image_name', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['pdf_id'], ['pdfs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('docu_category',
    sa.Column('docu_id', sa.BigInteger(), nullable=True),
    sa.Column('category_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['docu_id'], ['pdfs.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('docu_category')
    op.drop_table('images')
    op.drop_table('docu_user')
    op.drop_table('categories')
    op.drop_table('users')
    op.drop_table('pdfs')
    # ### end Alembic commands ###
