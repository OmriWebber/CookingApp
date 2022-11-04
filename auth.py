from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user
from models import Users, db

auth = Blueprint('auth', __name__, url_prefix='/auth')

# Register Route
@auth.route('/register', methods=('GET', 'POST'))
def register():
    msg = ''
    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # query
        user = Users.query.filter_by(username=username).first()
        
        if user:
            msg = 'Username already exists!'
            return render_template('auth/register.html',  msg=msg, name='Cooking App')

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = Users(username=username, email=email, password=generate_password_hash(password, method='sha256'))
        
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',  msg=msg, name='Cooking App')


@auth.route('/login', methods=('GET', 'POST'))
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        user = Users.query.filter_by(username=username).first()
        
        if user is None:
            msg = 'Username dosnt exist. Please try again '
        elif not check_password_hash(user.password, password):
            msg = 'Incorrect password.'
        elif user:
            # Create session data, we can access this data in other routes
            login_user(user, remember=True)
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            
        print(msg)

    return render_template('auth/login.html', msg=msg, name='Cooking App')
   

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
