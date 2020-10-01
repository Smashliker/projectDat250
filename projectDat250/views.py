from projectDat250 import app
from projectDat250 import query_db
from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from . import db
from . import models
import os
@app.route('/')
def index():
    test = query_db('SELECT * FROM users')
    return render_template('index.html', test=test)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = os.urandom(16)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username placeholder="Username">
            <p><input type=password name=password placeholder=Password>
            <p><input type=submit value=Login>
        </form>
    '''

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
            hashed = bcrypt.generate_password_hash(request.form['password'])
            user = User(username=request.form['username'], password=hashed, userid = generateUserID)
            db,session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        return '''
            <form method="post">
                <p><input type="text" name=username placeholder="Username">
                <p><input type="password" name=password placeholder="Password">
                <p><input type="password" name=password placeholder="Repeat Password">
                <p><input type="submit" value="Create User">
            '''
    else:
        return redirect(url_for('index'))
    
def validateUsername(wantedName):
    validated = True
    for username in db.query_db('select username from users'):
        if wantedName == username:
            validated = False
            break
    return validated
    
def generateUserID():
    while True:
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))

        for userid in db.query_db('select userid from users'):
            if result_str == userid:
                break
        return result_str 
                
        
