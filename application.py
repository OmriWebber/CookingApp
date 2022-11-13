from flask import Flask, render_template, request, redirect, jsonify, Markup, url_for, flash
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from models import *
from flask_ckeditor import CKEditor
import os, json, pymysql

pymysql.install_as_MySQLdb()

UPLOAD_FOLDER = 'static/img/recipeImages/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

application = Flask(__name__)
application.secret_key = 'dev'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ckeditor = CKEditor(application)

# If application detects rds database, use cloud database, if not use localhost
if 'RDS_DB_NAME' in os.environ:
    RDS_Connection_String = 'mysql://' + os.environ['RDS_USERNAME'] + ':' + os.environ['RDS_PASSWORD'] + '@' + os.environ['RDS_HOSTNAME'] + ':' + os.environ['RDS_PORT'] + '/' + os.environ['RDS_DB_NAME']
    print(RDS_Connection_String)
    print('TESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSETTESTSETSETSETSETSETSETSETSETSET')
    application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:password@cooking-app-database.ch0or1bnad8y.ap-southeast-2.rds.amazonaws.com:3306/cooking_app_db'
else:
    application.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost:3306/cookingapp"

db.init_app(application)
migrate = Migrate(application, db)

# Init Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(application)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# blueprint for auth routes in our application
from auth import auth as auth_blueprint
application.register_blueprint(auth_blueprint)

def allowed_file(filename):     
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def logThis(function, user, userID, recipe, recipeID):
    date = datetime.now()
    dateString = str(date)
    tuple = ('[',dateString,'] ',user,':',userID,' ',function,' ',recipe,':',recipeID)
    log = "".join(map(str, tuple))
    with open("log.txt", "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0 :
            file_object.write("\n")
        file_object.write(log)

def populate():
    f = open('dataset.json')
    data = json.load(f)
    
    for i in data:
        title = i['title']
        category = i['category']
        method = i['method']
        ingredients = i['ingredients']
        
        
        imageURL = i['imageURL']
        prepTime = i['prepTime']
        cookTime = i['cookTime']
        recipe = Recipes(title=title,category=category,method=method,imageURL=imageURL,prepTime=prepTime,cookTime=cookTime)
        
        ingredientsList = ingredients.split("\n")
        for ingredientName in ingredientsList:
            ingredient = Ingredients(name=ingredientName)
            recipe.ingredients.append(ingredient)
        
        db.session.add(recipe)
        
        
    db.session.commit()
    f.close()


@application.route("/")
def index():
    # populate()
    recipes=Recipes.query.all()
    return render_template("index.html", recipes=recipes, name="Cooking App", user=current_user)


@application.route("/createRecipe", methods=["POST", "GET"])
@login_required
def createRecipe():
    if request.method == "POST":
        # store values recieved from HTML form in local variables
        title=request.form.get("title")
        method=request.form.get("ckeditor")
        category=request.form.get("category")
        servings=request.form.get("servings")
        prepTime=request.form.get("prepTime")
        cookTime=request.form.get("cookTime")
        count=request.form.get("count")
        imageURLforDB='img/recipeImages/default.jpg'
        
        if 'recipeImage' not in request.files:
            print("No file part")
        file=request.files['recipeImage']
        if file.filename == '':
            print("No selected file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            imageURL = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            imageURLforDB = os.path.join('img/recipeImages/', filename)
            file.save(imageURL)
        
        recipe = Recipes(title=title,method=method,category=category,imageURL=imageURLforDB,servings=servings,prepTime=prepTime,cookTime=cookTime)
        
        for x in range(int(count)):
            ingredientIdentifier = 'ingredient-' + str(x+1)
            ingredientName = request.form.get(ingredientIdentifier)
            ingredient = Ingredients(name=ingredientName)
            recipe.ingredients.append(ingredient)

        db.session.add(recipe)
        db.session.commit()
        flash('Recipe Created.')
        return redirect(url_for('index'))
    recipes=Recipes.query.all()
    return render_template("createRecipe.html", recipes=recipes, name="Cooking App", user=current_user)


@application.route("/showRecipe/<id>")
def showRecipe(id):
    recipe=Recipes.query.filter_by(id=id).one()
    methodMarkup = Markup(recipe.method)
    ingredientIDs = []
    for ingredient in recipe.ingredients:
        ingredientIDs.append(ingredient.ingredient_id)
        
    return render_template("showRecipe.html", recipe=recipe, ingredientIDs=ingredientIDs, method=methodMarkup, name="Cooking App", user=current_user)


@application.route("/deleteRecipe/<id>")
@login_required
def deleteRecipe(id):
    recipe = Recipes.query.filter_by(id=id).one()
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe Deleted')
    
    logThis("deleted", current_user.username, current_user.id, recipe.title, recipe.id)
    return redirect(url_for('index'))

@application.route("/profile")
@login_required
def profile():
    user = Users.query.filter_by(id=current_user.id).first()

    return render_template('profile.html', user=user, name="Cooking App")


@application.route("/saveRecipe/<id>")
@login_required
def saveRecipe(id):
    user = Users.query.filter_by(id=current_user.id).first()
    recipe = savedUserRecipes(RecipeID=id)
    user.savedRecipes.append(recipe)
    db.session.commit()
    flash('Recipe Saved')

    return redirect(url_for('index'))

    
@application.route("/savedRecipes")
@login_required
def savedRecipes():
    savedRecipes = current_user.savedRecipes
    recipes = []
    for recipe in savedRecipes:
        recipe = db.session.query(Recipes).filter_by(id = recipe.RecipeID).all()
        recipes += recipe
    return render_template('savedRecipes.html', recipes=recipes, user=current_user, name="Cooking App")


@application.route("/editRecipe/<id>", methods=["POST", "GET"])
@login_required
def editRecipe(id):
    recipe = Recipes.query.filter_by(id=id).first()
    if request.method == "POST":
        # store values recieved from HTML form in local variables
        recipe.title=request.form.get("title")
        recipe.method=request.form.get("ckeditor")
        recipe.category=request.form.get("category")
        recipe.servings=request.form.get("servings")
        recipe.prepTime=request.form.get("prepTime")
        recipe.cookTime=request.form.get("cookTime")
        count=request.form.get("count")
        
        if 'recipeImage' not in request.files:
            print("No file part")
        file=request.files['recipeImage']
        if file.filename == '':
            print("No selected file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            imageURL = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            imageURLforDB = os.path.join('img/recipeImages/', filename)
            recipe.imageURL = imageURLforDB
            file.save(imageURL)
    
        for x in range(int(count)):
            ingredientIdentifier = 'ingredient-' + str(x+1)
            ingredientName = request.form.get(ingredientIdentifier)
            ingredient = Ingredients(name=ingredientName)
            checkIngredients = Ingredients.query.filter_by(name=ingredient.name).all()
            if checkIngredients:
                
                for checkIngredient in checkIngredients:
                    print(checkIngredient)
                    if checkIngredient == ingredient.name:
                        recipe.ingredients.remove(ingredient)
                    print('Ingredient Already Exists')
            else:
                recipe.ingredients.append(ingredient)

        db.session.commit()
        flash('Recipe Edited.')
        return redirect(url_for('showRecipe', id=id))
    return render_template('editRecipe.html', recipe=recipe, user=current_user, name="Cooking App")


@application.route("/mealPlanner")
@login_required
def mealPlanner():
    recipes = Recipes.query.all()
    return render_template('mealPlanner.html', recipes=recipes, user=current_user, name="Cooking App")


@application.route("/addToShoppingList/<ingredientIDs>")
@login_required
def addToShoppingList(ingredientIDs):
    user = Users.query.filter_by(id=current_user.id).first()
    
    
    strippedString = ingredientIDs.lstrip("[").rstrip("]")
    ingredients = strippedString.split(', ')
    
    def exists(ingredient):
        for shoppingList in user.shoppingList:
            if shoppingList.ingredient == ingredient.name:
                return True
        return False
        
    for ingredientID in ingredients:
        ingredient = Ingredients.query.filter_by(ingredient_id=ingredientID).one()
        if exists(ingredient):
            print('already exists')
        else:
            print('adding item')
            shoppingListItem = shoppingList(ingredient=ingredient.name)
            user.shoppingList.append(shoppingListItem)
    
    flash('Ingredients added to shopping list')
    db.session.commit()
    return redirect(url_for('index'))

@application.route("/shoppingList")
@login_required
def showShoppingList():
    shoppingList = current_user.shoppingList
    print(shoppingList)
    return render_template('shoppingList.html', user=current_user, shoppingList=shoppingList, name="Cooking App")


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
    



  