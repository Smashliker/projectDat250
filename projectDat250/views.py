from projectDat250 import app, query_db, get_db
from flask import Flask, render_template, redirect, url_for, request, session
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import string, random
from projectDat250 import get_db, Users, db, LoginForm, FriendForm
from projectDat250 import SignUpForm, PostForm
from flask_login import login_required, logout_user, current_user, login_user
#from flask_bcrypt import Bcrypt
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
import os


@app.route('/')
def index():
    if hasattr(current_user, 'username') == False:
        return redirect(url_for('login'))
    
    for post in query_db("SELECT created FROM post"):
        app.logger.info(post["created"])

    userid = "djfnj"
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
    #Create a WTForm for login
    form = LoginForm()
    if form.validate_on_submit():
        userid = 0

        #Check for the username in the database to find a valid user
        for user in query_db("SELECT * FROM users"):
            if user["username"] == request.form["username"]:
                userid = user["userid"]

        #Find/Create the user object by query
        user = Users.query.filter_by(userid=userid).first()
        
        #If the user exists
        if user:
            #Verify inputted password with the hashed version in the database
            if sha256_crypt.verify(request.form["password"], user.password):
                #Add to session using flask_login
                user.authenicated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                #flash('Logged in successfully.')
                return redirect(url_for('index'))
    return render_template('login.html', form=form)

#@app.route('/logout')
#def logout():
#    # remove the username from the session if it's there
#    session.pop('username', None)
#    return redirect(url_for('index'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
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
    #Create WTForm for signup
    form = SignUpForm()
    if form.validate_on_submit():
        #Validate usernamee by query database to check if someone else has already claimed the username
        if validateUsername(request.form['username']) is True and len(request.form['password']) >= 1:
            #Generate a non-incremental user ID
            userid = generateUserID()

            #Set username and password, and has the password
            username = request.form['username']
            password = str(sha256_crypt.hash(request.form['password']))
            
            #Create Users object and add it to the database
            user = Users(username=username, password=password, userid = userid)
            db.session.add(user)
            db.session.commit()
        else:
            return "error"
        return redirect(url_for('index'))
    return render_template('createUser.html', form=form)

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    #Create WTForm for posting
    form = PostForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.instance_path, 'photo', filename
        ))
        #Add post to post table in database
        query_db(f'INSERT INTO POST (author_id,author_name,title,body,image_path) VALUES ("{current_user.userid}","{current_user.username}","{request.form["title"]}","{request.form["body"]}","{"instance/photo/" + filename}")')
        get_db().commit()
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


#Validates username by querying the database and checking if there is anyone else with that exact username (Case Sensitive)
def validateUsername(wantedName):
    validated = True
    for user in query_db('SELECT username FROM users'):
        if wantedName == user["username"]:
            validated = False
            break
    return validated

#Generate a user id by adding random letters together
#TODO: Include numbers in the generation as well
def generateUserID():
    while True:
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(8))

        for userid in query_db('select userid from users'):
            if result_str == userid:
                break
        return result_str 