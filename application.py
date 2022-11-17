from flask import Flask, render_template, request, redirect, jsonify, Markup, url_for, flash
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_ckeditor import CKEditor
from flask_cdn import CDN
import os, json, pymysql

from models import *

pymysql.install_as_MySQLdb()

UPLOAD_FOLDER = 'static/img/recipeImages/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

application = Flask(__name__)
application.secret_key = 'dev'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['CDN_DOMAIN'] = 'dk2cs70wwok20.cloudfront.net'
application.config['CDN_TIMESTAMP'] = False

ckeditor = CKEditor(application)

# If application detects rds database, use cloud database, if not use localhost
if 'RDS_HOSTNAME' in os.environ:
    print('AWS ELB ENV DETECTED')
    CDN(application)
    RDS_Connection_String = 'mysql+pymysql://' + os.environ['RDS_USERNAME'] + ':' + os.environ['RDS_PASSWORD'] + '@' + os.environ['RDS_HOSTNAME'] + ':' + os.environ['RDS_PORT'] + '/' + os.environ['RDS_DB_NAME']
    application.config['SQLALCHEMY_DATABASE_URI'] = RDS_Connection_String
else:
    print('LOCAL ENV DETECTED')
    application.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost:3306/cookingapp"

db.init_app(application)
migrate.init_app(application, db)

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
    
def reverse_readline(filename, buf_size=8192):
    # A generator that returns the lines of a file in reverse order
    with open(filename) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first 
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment


@application.route("/")
def index():
    # populate()    # Uncomment this line to populate database with test data.
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
        
        # Image Handling
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
        
        # Creating Recipe Object
        recipe = Recipes(title=title,
                         method=method,
                         category=category,
                         imageURL=imageURLforDB,
                         servings=servings,
                         prepTime=prepTime,
                         cookTime=cookTime)
        
        # Populating Recipe with user submitted ingredients
        for x in range(int(count)):
            ingredientIdentifier = 'ingredient-' + str(x+1)
            ingredientName = request.form.get(ingredientIdentifier)
            ingredient = Ingredients(name=ingredientName)
            recipe.ingredients.append(ingredient)

        # Adding and commiting new recipe to database
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe Created.')
        return redirect(url_for('index'))
    return render_template("createRecipe.html", name="Cooking App", user=current_user)


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
    skip = Users.query.filter_by(id=current_user.id).first()
    users = Users.query.all()
        
    logs = []
    for line in reversed(list(open("log.txt"))):
        logs.append(line.rstrip())

    savedRecipes = current_user.savedRecipes
    userRecipes = []
    for recipe in savedRecipes:
        recipe = db.session.query(Recipes).filter_by(id = recipe.RecipeID).all()
        userRecipes += recipe
        
    shoppinglist = current_user.shoppingList
    
    return render_template('profile.html', user=current_user, logs=logs, shopping_list=shoppinglist, user_recipes=userRecipes, user_list=users, skip=skip, name="Cooking App")


@application.route("/makeAdmin/<id>")
@login_required
def makeAdmin(id):
    if current_user.is_Admin:
        user = Users.query.filter_by(id=id).first()
        print(user)
        user.is_Admin = True
        db.session.commit()
        logThis("Made Admin", current_user.username, current_user.id, user.username, user.id)
        flash(user.username + ' is now an Admin')
    else:
        flash('You need to be admin to do that!')
    return redirect(url_for('profile'))


@application.route("/revokeAdmin/<id>")
@login_required
def revokeAdmin(id):
    if current_user.is_Admin:
        user = Users.query.filter_by(id=id).first()
        print(user)
        user.is_Admin = False
        db.session.commit()
        logThis("Revoked Admin", current_user.username, current_user.id, user.username, user.id)
        flash(user.username + ' is no longer an Admin')
    else:
        flash('You need to be admin to do that!')
    return redirect(url_for('profile'))


@application.route("/saveRecipe/<id>")
@login_required
def saveRecipe(id):
    user = Users.query.filter_by(id=current_user.id).first()
    saveRecipe = savedUserRecipes(userID=user.id, RecipeID=id)
    checkIfExists = savedUserRecipes.query.filter_by(userID=user.id, RecipeID=saveRecipe.RecipeID).first()
    if checkIfExists:
        flash('Recipe Already Saved')
        print(checkIfExists)
    else:
        user.savedRecipes.append(saveRecipe)
        db.session.commit()
        flash('Recipe Saved')
    return redirect(url_for('showRecipe', id=id))

@application.route("/unsaveRecipe/<id>")
@login_required
def unsaveRecipe(id):
    user = Users.query.filter_by(id=current_user.id).first()
    unsaveRecipe = savedUserRecipes.query.filter_by(userID=user.id, RecipeID=id).first()
    if not unsaveRecipe:
        flash('Recipe Not Saved')
        print(unsaveRecipe)
    else:
        user.savedRecipes.remove(unsaveRecipe)
        db.session.commit()
        recipe = Recipes.query.filter_by(id=unsaveRecipe.RecipeID).first()
        flashmsg = 'Removed ' + recipe.title + ' from saved recipes.'
        flash(flashmsg)
    return redirect(url_for('profile'))

    
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
    return redirect(url_for('showShoppingList'))


@application.route("/removeFromShoppingList/<id>")
@login_required
def removeFromShoppingList(id):
    user = Users.query.filter_by(id=current_user.id).first()
    shoppingListItem = shoppingList.query.filter_by(id=id).first()
    if shoppingListItem:
        user.shoppingList.remove(shoppingListItem)
        db.session.commit()
        flashmsg = 'Removed ' + shoppingListItem.ingredient + ' from shopping list'
        flash(flashmsg)
    else:
        flashmsg = 'Ingredient not Found'
        flash(flashmsg)
    return redirect(url_for('showShoppingList'))


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
    



  