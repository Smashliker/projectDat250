from projectDat250 import app, query_db, get_db, get_db, Users, db, LoginForm, FriendForm, SignUpForm, PostForm, CommentForm
from flask import Flask, render_template, redirect, url_for, request, session, flash, Response
from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms.validators import DataRequired
import string, random
from flask_login import login_required, logout_user, current_user, login_user
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from datetime import datetime
import os

def sortPostKey(x):
    return x["id"]

def sortFriendKey(x):
    return x["username"]

def checkIfRepost(postTekst):
    postTekst = postTekst.replace(" ","") #Fjerner whitespace og gjør alt lowercase
    postTekst = postTekst.strip("\n")
    postTekst = postTekst.lower()

    maks = query_db("SELECT * FROM post") #Finner maksverdi
    maksverdi = maks[-1]["id"]

    starten = 0
    grense = 50
    if maksverdi > grense:          #Setter startverdi for sjekk
        starten = maksverdi - grense

    postene = query_db(f"SELECT * FROM post LIMIT {starten},{maksverdi}")

    for post in postene:
        body = post["body"]
        body = body.replace(" ","")
        body = body.strip("\n")
        body = body.lower()

        i = 0
        plag = 0
        prosentPlag = 0.0

        if len(body) < 10 or len(postTekst) < 10:   #Hvis en av strengene ikke passer inn i 9/10 forholdet vi har, bruk en enklere sammenlikning
            if body == postTekst:
                return True
            
        else:
            prosentGrense = 0.90

            if len(body) >= len(postTekst): #Dette sikrer at metoden ikke monopoliserer visse bokstaver
                lengden = len(body)
            else:
                lengden = len(postTekst)

            for ordet in body:
                if i >= len(postTekst): #Siden postene kan ha forskjellig lengde, sjekker denne at vi ikke får error
                    break

                if postTekst[i] == ordet: #ved at én bokstav er lik:
                    plag += 1
                    prosentPlag = plag/lengden
                    if prosentPlag >= prosentGrense:
                        return True

                i += 1
    return False

@app.route('/')
def index():
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))

    #TODO: Figure this out:
    #Testing response, not sure what to add as argument for Response function
    response = Response()
    response.headers['Content-Security-Policy'] = "default-src 'self'"

    userid = current_user.userid
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
    postliste += query_db(f"SELECT * FROM post WHERE author_id = '{userid}'")
    postliste.sort(reverse=True, key=sortPostKey)
    venneliste.sort(key=sortFriendKey)

    return render_template('index.html', venneliste=venneliste, postliste=postliste)

# Set the secret key to some random bytes
app.secret_key = os.urandom(16)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #Logout user if already logged in
    if current_user.is_authenticated:
        logout_user


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
                response = make_response(redirect(url_for('index')))
                response.headers['Content-Security-Policy'] = "default-src 'self'"

                return response
    response = make_response(render_template('login.html', form=form))
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

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
    userid = current_user.userid
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
        if validateUsername(request.form['username']) is True:
            #Generate a non-incremental user ID
            userid = generateUserID()

            #Set username and password, and has the password
            username = request.form['username']
            password = str(sha256_crypt.hash(request.form['password']))
            
            #Create Users object and add it to the database
            user = Users(username=username, password=password, userid = userid)

            adminQ = query_db("SELECT * FROM users WHERE username='Admin'")
            adminID = adminQ[0]["userid"]   #TODO evaluer om denne metoden er sikker, eller om den setter superbrukeren i risiko
            query_db(f"INSERT INTO friends (userid,friendid) VALUES('{userid}','{adminID}')") 
            get_db().commit() #Poenget med koden er å legge til en superbruker slik at det alltid er en venn

            db.session.add(user)
            db.session.commit()
        else:
            return "ERROR: user already exists!"
        return redirect(url_for('index'))
    return render_template('createUser.html', form=form)

@app.route('/createPost', methods=['GET', 'POST'])
@login_required
def createPost():
    #Create WTForm for posting
    form = PostForm()
    if form.validate_on_submit():
        f = form.photo.data
        app.logger.info(f)
        nu = datetime.now()
        tidNu = nu.strftime("%d/%m/%Y  %H:%M:%S")
        if checkIfRepost(request.form["body"]):
            return "ERROR: post has been deemed a repost!"
        elif f != None:
            filename = secure_filename(f.filename)
            f.save(os.path.join(
                app.root_path, 'static', filename
            ))
            query_db(f'INSERT INTO POST (author_id,author_name,created,title,body,image_path) VALUES ("{current_user.userid}","{current_user.username}","{tidNu}","{request.form["title"]}","{request.form["body"]}","{filename}")')
        else:
            query_db(f'INSERT INTO POST (author_id,author_name,created,title,body) VALUES ("{current_user.userid}","{current_user.username}","{tidNu}","{request.form["title"]}","{request.form["body"]}")')
        #Add post to post table in database
        get_db().commit()
        return redirect(url_for('index'))
    return render_template('createPost.html', form=form)


@app.route('/<int:post_id>')
#@login_required
def viewPosts(post_id):
    post = query_db(f'SELECT * FROM post WHERE id={post_id}')
    comments = query_db(f"SELECT * FROM comments WHERE post_id={post_id}")
    return render_template('viewPost.html', post=post[0], comments=comments)

@app.route('/<int:post_id>/comment', methods=["GET", "POST"])
#@login_required
def comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        splitRequest = request.path.split('/')

        f = open("tmp", "r")
        post_id = int(f.read())
        f.close()
        
        body = request.form['body']
        query_db(f'INSERT INTO comments (post_id,author_id,author_name,body) VALUES("{post_id}","{current_user.userid}","{current_user.username}", "{body}")')
        get_db().commit()
        return redirect(url_for('index'))

    f = open("tmp", "w")
    f.write(str(post_id))
    f.close
    return render_template('comment.html', form=form)


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
#TODO: FIX SO IT WORKS AS INTENDED (CAN GET SAME USER ID)
def generateUserID():
    while True:
        letters = string.ascii_lowercase
        for x in range(9):
            letters += str(x)
        result_str = ''.join(random.choice(letters) for i in range(8))

        for userid in query_db('select userid from users'):
            if result_str == userid:
                break
        return result_str 