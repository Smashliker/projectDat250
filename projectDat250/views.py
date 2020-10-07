from projectDat250 import app, query_db, get_db
from flask import Flask, render_template, redirect, url_for, request, session
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import string, random
from projectDat250 import get_db, Users, db, LoginForm, FriendForm
from flask_login import login_required, logout_user, current_user, login_user
#from flask_bcrypt import Bcrypt
from passlib.hash import sha256_crypt
import os


@app.route('/')
def index():
    userid = "djfnj"    #placeholder for hva enn useriden skal være, for testing
    venneliste = query_db(f"SELECT * FROM friends WHERE userid = '{userid}'")
    venneIDliste = []
    for pers in venneliste:
        venneIDliste.append(pers['friendid'])
    #I koden over finner vi id'ene til vennene til brukeren, hvor brukeren er userid

    venneliste = [] 
    postliste = []
    for ID in venneIDliste: #Merk hvor nyttig det er å concatenate listen på denne måten
        venneliste += query_db(f"SELECT * FROM users WHERE userid = '{ID}'")
        postliste += query_db(f"SELECT * FROM post WHERE author_id = '{ID}'")

    return render_template('index.html', venneliste=venneliste, postliste=postliste)


#mest for forståelsen at this point
@app.route('/gibFriends')
def gibFriends():
    tester = query_db('INSERT INTO "friends" ("userid","friendid") VALUES("djfnj", "asdasd")')
    get_db().commit()
    return redirect(url_for('index'))


# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = os.urandom(16)

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        userid = 0
        for user in query_db("SELECT * FROM users"):
            if user["username"] == request.form["username"]:
                userid = user["userid"]

        user = Users.query.filter_by(userid=userid).first()
        app.logger.info(user.username)
        if user:
            if sha256_crypt.verify(request.form["password"], user.password):
                user.authenicated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                flash('Logged in successfully.')
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

@app.route('/newFriend', methods=['GET', 'POST'])
def newFriend():
    userid = "djfnj"    #placeholder
    formen = FriendForm()

    addResult = None   #0 indikerer at brukeren ble lagt til vennelisten, 1 at brukeren ikke ble funnet, og 2 at brukeren allerede er i vennelisten, og None at det er usikkert
    if formen.validate_on_submit():

        tempFriendID = None
        for user in query_db("SELECT * FROM users"):
            if user["username"] == request.form["friendName"]:
                tempFriendID = user["userid"]
                break
        
        for friend in query_db(f"SELECT * FROM friends WHERE userid='{userid}'"):
            if tempFriendID == friend["friendid"]:
                addResult = 2

        if addResult == None and tempFriendID != None:
            query_db(f"INSERT INTO friends (userid,friendid) VALUES('{userid}','{tempFriendID}')")
            get_db().commit()
            addResult = 0
        elif addResult != 2:
            addResult = 1

    return render_template('newFriend.html', form=formen, addResult=addResult)


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
                
        

