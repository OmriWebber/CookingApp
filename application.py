from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from models import *
import os
import pymysql

pymysql.install_as_MySQLdb()

UPLOAD_FOLDER = 'static/img/recipeImages/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

application = Flask(__name__)
application.secret_key = 'dev'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# If application detects rds database, use cloud database, if not use localhost
if 'RDS_DB_NAME' in os.environ:
    application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:password@contact-app-database.ch0or1bnad8y.ap-southeast-2.rds.amazonaws.com:3306/contact_app_db'
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


@application.route("/")
def index():
    recipes=Recipes.query.all()
    print(recipes[4].ingredients)
    return render_template("index.html", recipes=recipes, name="Cooking App", user=current_user)


@application.route("/createRecipe", methods=["POST", "GET"])
@login_required
def createRecipe():
    if request.method == "POST":
        # store values recieved from HTML form in local variables
        title=request.form.get("title")
        method=request.form.get("method")
        imageURL=request.form.get("imageurl")
        category=request.form.get("category")
        prepTime=request.form.get("preptime")
        cookTime=request.form.get("cooktime")
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
        
        recipe = Recipes(title=title,method=method,category=category,imageURL=imageURLforDB,prepTime=prepTime,cookTime=cookTime)
        
        for x in range(int(count)):
            ingredientIdentifier = 'ingredient-' + str(x+1)
            ingredientName = request.form.get(ingredientIdentifier)
            ingredient = Ingredients(name=ingredientName)
            recipe.ingredients.append(ingredient)


        db.session.add(recipe)
        
        db.session.commit()
        msg="added recipe"
        print(msg)
    recipes=Recipes.query.all()
    return render_template("createRecipe.html", recipes=recipes, name="Cooking App", user=current_user)


@application.route("/showRecipe/<id>")
def showRecipe(id):
    # select row from contacts table for contact ID passed from main page
    recipe=Recipes.query.filter_by(id=id).one()
    return render_template("showRecipe.html", recipe=recipe, name="Cooking App", user=current_user)


@application.route("/deleteRecipe/<id>")
def deleteRecipe(id):
    # select row from contacts table for contact ID passed from main page
    recipe = Recipes.query.filter_by(id=id).one()
    db.session.delete(recipe)
    db.session.commit()
    logThis("deleted", current_user.name, current_user.id, recipe.title, recipe.id)
    return redirect(url_for('index'))

@application.route("/profile")
def profile():
    return render_template('profile.html')

@application.route("/savedRecipes")
def savedRecipes():
    return render_template('savedRecipes.html')


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
    



  