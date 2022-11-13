"""deployment

Revision ID: 843a3b83a189
Revises: 
Create Date: 2022-11-14 08:55:40.356864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '843a3b83a189'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Recipes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.Column('method', sa.Text(), nullable=True),
    sa.Column('imageURL', sa.String(length=200), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('prepTime', sa.String(length=50), nullable=True),
    sa.Column('cookTime', sa.String(length=50), nullable=True),
    sa.Column('servings', sa.String(length=50), nullable=True),
    sa.Column('dateCreated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('is_Admin', sa.Boolean(), nullable=False),
    sa.Column('dateCreated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Ingredients',
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id'], ['Recipes.id'], ),
    sa.PrimaryKeyConstraint('ingredient_id')
    )
    op.create_table('savedUserRecipes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userID', sa.Integer(), nullable=True),
    sa.Column('RecipeID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['userID'], ['Users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shoppingList',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('ingredient', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shoppingList')
    op.drop_table('savedUserRecipes')
    op.drop_table('Ingredients')
    op.drop_table('Users')
    op.drop_table('Recipes')
    # ### end Alembic commands ###
