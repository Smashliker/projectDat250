from projectDat250 import app
from projectDat250 import query_db
from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import string, random
from projectDat250 import get_db, Users, db, LoginForm
#from flask_bcrypt import Bcrypt
from passlib.hash import sha256_crypt
import os


@app.route('/')
def index():
    test = query_db('SELECT * FROM users')
    return render_template('index.html', test=test)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = os.urandom(16)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is

    form = LoginForm()
    if form.validate_on_submit():
        userid = 0
        for user in query_db("SELECT * FROM users"):
            if user["username"] == request.form["username"]:
                userid = user["userid"]

        user = Users.query.filter_by(userid=userid).first()
        if user:
            if sha256_crypt.verify(request.form["password"], user.password):
                app.logger.info(user['username'])
                user.authenicated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                flask.flash('Logged in successfully.')
                return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')


@app.route('/createUser', methods=['GET', 'POST'])
def createUser():
    if request.method == 'POST':
        if validateUsername(request.form['username']) is True and len(request.form['password']) >= 1:
            #TODO: Actually create user object from class in db.py
            userid = generateUserID()
            username = request.form['username']
            password = str(sha256_crypt.hash(request.form['password']))
            user = Users(username=username, password=password, userid = userid)
            db.session.add(user)
            db.session.commit()
        else:
            return "error"
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type="text" name=username placeholder="Username">
            <p><input type="password" name=password placeholder="Password">
            <p><input type="password" name=password placeholder="Repeat Password">
            <p><input type="submit" value="Create User">
        '''

def validateUsername(wantedName):
    validated = True
    for username in query_db('select username from users'):
        if wantedName == username:
            validated = False
            break
    return validated
    
def generateUserID():
    while True:
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(8))

        for userid in query_db('select userid from users'):
            if result_str == userid:
                break
        return result_str 
                
        
