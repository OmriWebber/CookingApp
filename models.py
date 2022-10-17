from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, Table, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Users Table Model
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(10), nullable=False)
    recipes = relationship("savedRecipes")
    is_Admin = Column(Boolean, nullable=False, default=False)
    dateCreated = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        template = '{0.id} {0.name} {0.is_Admin} {0.date_created}'
        return template.format(self)

# Recipes Table Model
class Recipes(db.Model):
    __tablename__= "Recipes"
    recipeID = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    method = Column(String(500), nullable=True)
    imageURL = Column(String(200), nullable=True)
    category = Column(String(50), nullable=True)
    prepTime = Column(String(20), nullable=True)
    cookTime = Column(String(20), nullable=True)
    ingredients = relationship("recipeIngredients")
    
    def __repr__(self):
        template = '{0.recipeID} {0.title}'
        return template.format(self)

# recipeIngredients Table Model
class recipeIngredients(db.Model):
    __tablename__= "recipeIngredients"
    id = Column(Integer, primary_key=True)
    recipeID = Column(Integer, ForeignKey("Recipes.recipeID"))
    
    def __repr__(self):
        template = '{0.recipeID} {0.name}'
        return template.format(self)
    
# Ingredients Table Model
class Ingredients(db.Model):
    __tablename__= "Ingredients"
    ingredientID = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    categor = Column(String(100), nullable=True)
    
    def __repr__(self):
        template = '{0.recipeID} {0.title}'
        return template.format(self)
    
    
    
    
# SavedRecipes Table Model
class savedRecipes(db.Model):
    __tablename__= "savedRecipes"
    id = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey("Users.id"))
    RecipeID = Column(Integer)
    
    def __repr__(self):
        template = '{0.id} {0.userID}'
        return template.format(self)
    
    