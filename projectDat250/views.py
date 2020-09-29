from projectDat250 import app
from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import os
@app.route('/')
def index():
    return render_template('index.html')

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = os.urandom(16)

@app.route('/login', methods=['GET', 'POST'])
def login():
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