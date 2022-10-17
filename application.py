from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import *
import os

application = Flask(__name__)

application.secret_key = 'dev'

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if 'RDS_DB_NAME' in os.environ:
    application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:password@contact-app-database.ch0or1bnad8y.ap-southeast-2.rds.amazonaws.com:3306/contact_app_db'
else:
    print("test")
    # application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:password@contact-app-database.ch0or1bnad8y.ap-southeast-2.rds.amazonaws.com:3306/contact_app_db'
    application.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

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

def logThis(function, user, userID, contact, contactID):
    date = datetime.now()
    dateString = str(date)
    tuple = ('[',dateString,'] ',user,':',userID,' ',function,' ',contact,':',contactID)
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
    return render_template("index.html", recipes=recipes, name="Cooking App", user=current_user)



@application.route("/createRecipe", methods=["POST"])
@login_required
def addContact():
    #store values recieved from HTML form in local variables
    title=request.form.get("FirstName")
    method=request.form.get("LastName")
    imageURL=request.form.get("MiddleName")
    category=request.form.get("WorkCompany")
    prepTime=request.form.get("WorkJobTitle")
    cookTime=request.form.get("Mobile")
    ingredients=request.form.get("HomePhone")
    
    # Pass on the local values to the corresponding model
    recipe = Recipes( title=title,method=method,imageURL=imageURL,category=category,prepTime=prepTime,cookTime=cookTime,ingredients=ingredients)
    db.session.add(recipe)
    db.session.commit()
    recipes=Recipes.query.all()
    return redirect(url_for('index'))
    

@application.route("/showRecipe/<id>")
def showContact(id):
    # select row from contacts table for contact ID passed from main page
    recipe=Recipes.query.filter_by(RecipeID=id).one()
    return render_template("showRecipe.html", recipe=recipe, name="Cooking App", user=current_user)


@application.route("/deleteRecipe/<id>")
def deleteContact(id):
    # select row from contacts table for contact ID passed from main page
    recipe = Recipes.query.filter_by(recipeID=id).one()
    db.session.delete(recipe)
    db.session.commit()
    logThis("deleted", current_user.name, current_user.id, recipe.title, recipe.recipeID)
    return redirect(url_for('index'))

@application.route("/profile")
def profile():
    return render_template('profile.html')


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
    



  