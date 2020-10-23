from projectDat250 import app, Users, db, LoginForm, FriendForm, SignUpForm, PostForm, CommentForm, Post, Comments, Friends, tmpObj
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import string, random
from flask_login import login_required, logout_user, current_user, login_user
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import select
import os


def sortPostKey(x):
    return x["id"]

def sortFriendKey(x):
    return x["username"]

def checkIfRepost(postTekst):
    postTekst = postTekst.replace(" ","") #Fjerner whitespace og gjør alt lowercase
    postTekst = postTekst.strip("\n")
    postTekst = postTekst.lower()

    maks = Post.query.all() #Finner maksverdi
    maksverdi = maks[-1].id

    starten = 0
    grense = 50
    if maksverdi > grense:          #Setter startverdi for sjekk
        starten = maksverdi - grense

    #postene = query_db(f"SELECT * FROM post LIMIT {starten},{maksverdi}")
    postene = Post.query.limit(grense).all()

    for post in postene:
        body = post.body
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
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    userid = current_user.userid
    venneliste = Friends.query.filter_by(userid=userid).all()
    venneIDliste = []
    for pers in venneliste:
        venneIDliste.append(pers.friendid)
    #I koden over finner vi id'ene til vennene til brukeren, hvor brukeren er userid

    venneliste = [] 
    postliste = []
    for ID in venneIDliste: #Merk hvor nyttig det er å concatenate listen på denne måten
        #venneliste += query_db(f"SELECT * FROM users WHERE userid = '{ID}'")
        #postliste += query_db(f"SELECT * FROM post WHERE author_id = '{ID}'")
        venneliste.append(Users.query.filter_by(userid=ID).first())
        postliste.append(Post.query.filter_by(author_id=ID).first())
    #postliste += query_db(f"SELECT * FROM post WHERE author_id = '{userid}'")
    postliste += Post.query.filter_by(author_id=userid)

    postliste.sort(reverse=True, key=lambda post: post.id)
    #postliste.sort(reverse=True, key=sortPostKey)
    venneliste.sort(key=lambda venn: venn.username)


    return render_template('index.html', venneliste=venneliste, postliste=postliste)

# Set the secret key to some random bytes
app.secret_key = os.urandom(16)

@app.route('/login', methods=['GET', 'POST'])
def login():
    status = 0
    #Logout user if already logged in
    if current_user.is_authenticated:
       logout_user

    #Create a WTForm for login
    form = LoginForm()
    if form.validate_on_submit():
        userid = 0

        #Check for the username in the database to find a valid user
        for user in Users.query.all():
            if user.username == request.form["username"]:
                userid = user.userid

        #Find/Create the user object by query
        user = Users.query.filter_by(userid=userid).first()

        if user:
            #Verify inputted password with the hashed version in the database
            if sha256_crypt.verify(request.form["password"], user.password):
                #Add to session using flask_login
                user.authenicated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=False)
                return redirect(url_for('index'))
            else:
                return render_template("error.html", error="Invalid username or password!")
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

@app.route('/newFriend', methods=['GET', 'POST'])
@login_required
def newFriend():
    userid = current_user.userid
    formen = FriendForm()

    addResult = None   #0 indikerer at brukeren ble lagt til vennelisten, 1 at brukeren ikke ble funnet, 2 at brukeren allerede er i vennelisten, 3 at vennen er lik bruker, og None at det er usikkert
    if formen.validate_on_submit():

        tempFriendID = None
        for user in Users.query.all():
            if user.username == request.form["friendName"]:
                tempFriendID = user.userid
                break
        
        for friend in Friends.query.filter_by(userid=userid).all():
            if tempFriendID == friend.friendid:
                addResult = 2

        if userid == tempFriendID:
            addResult = 3

        elif addResult == None and tempFriendID != None:
            friend = Friends()
            friend.userid = current_user.userid
            friend.friendid = tempFriendID
            db.session.add(friend)
            db.session.commit()
            #query_db(f"INSERT INTO friends (userid,friendid) VALUES('{userid}','{tempFriendID}')")
            #get_db().commit()
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

            #admin = Users.query.filter_by(username='Admin').first()
            #adminID = admin.userid  #TODO evaluer om denne metoden er sikker, eller om den setter superbrukeren i risiko
            #friend = Friends()
            #friend.userid = userid
            #friend.friendid = adminID
            #query_db(f"INSERT INTO friends (userid,friendid) VALUES('{userid}','{adminID}')") 
            #get_db().commit() #Poenget med koden er å legge til en superbruker slik at det alltid er en venn
            #db.session.add(friend)

            db.session.add(user)
            db.session.commit()
        else:
            return render_template('error.html', error="User already exists!")
        return redirect(url_for('index'))
    return render_template('createUser.html', form=form)

@app.route('/createPost', methods=['GET', 'POST'])
@login_required
def createPost():
    #Create WTForm for posting
    form = PostForm()
    if form.validate_on_submit():
        f = form.photo.data
        nu = datetime.now()
        tidNu = nu.strftime("%d/%m/%Y  %H:%M:%S")
        if checkIfRepost(request.form["body"]):
            return "ERROR: post has been deemed a repost!"
        post = Post()
        post.author_id = current_user.userid
        post.author_name = current_user.username
        post.created = tidNu
        post.title = request.form["title"]
        post.body = request.form["body"]
        if f != None:
            filename = secure_filename(f.filename)
            f.save(os.path.join(
                app.root_path, 'static', filename
            ))
            post.image_path = filename
        db.session.add(post)
        db.session.commit()
        #Add post to post table in database
        return redirect(url_for('index'))
    else:
        render_template("error.html", error="Missing title or body")
    return render_template('createPost.html', form=form)


@app.route('/<int:post_id>')
@login_required
def viewPosts(post_id):
    post = Post.query.filter_by(id=post_id).first()
    comments = Comments.query.filter_by(post_id=post_id).all()
    print(comments)
    #
    comments.sort(reverse=True, key=lambda post: post.id)
    return render_template('viewPost.html', post=post, comments=comments)

@app.route('/<int:post_id>/comment', methods=["GET", "POST"])
@login_required
def comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        splitRequest = request.path.split('/')

        nu = datetime.now()
        tidNu = nu.strftime("%d/%m/%Y  %H:%M:%S")
        tmp = tmpObj.query.filter_by(userid=current_user.userid)
        #tmp = query_db(f"SELECT * FROM tmp WHERE userid='{current_user.userid}'")
        post_id = tmp[0]['post_id']
        
        comment = Comments()
        comment.author_id = current_user.userid
        comment.author_name = current_user.username
        comment.post_id = post_id
        comment.body = request.form['body']
        comment.created = tidNu

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('index'))

    tmpliste = tmpObj.query.filter_by(userid=current_user.userid).all()
    if len(tmpliste) > 0:
        entry = tmpObj.query.filter_by(userid=current_user.userid)
        entry.post_id = post_id
        db.session.commit()
    else:
        entry = tempObj()
        entry.userid = current_user.userid
        entry.post_id = post_id
        db.session.add(entry)
        db.session.commit()
    get_db().commit()

    return render_template('comment.html', form=form)


#Validates username by querying the database and checking if there is anyone else with that exact username (Case Sensitive)
def validateUsername(wantedName):
    validated = True
    for user in Users.query.all():
        if wantedName.lower() == user.username.lower():
            validated = False
            break
    return validated

#Generate a user id by adding random letters together
#TODO: Include numbers in the generation as well
#TODO: FIX SO IT WORKS AS INTENDED (CAN GET SAME USER ID)
def generateUserID():
    duplicate = False
    while True:
        letters = string.ascii_lowercase
        for x in range(9):
            letters += str(x)
        result_str = ''.join(random.choice(letters) for i in range(8))

        if Users.query.filter_by(userid=str(result_str)).first() != None:
            continue

        return result_str 
