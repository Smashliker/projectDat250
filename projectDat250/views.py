from projectDat250 import app, Users, db, LoginForm, FriendForm, SignUpForm, PostForm, CommentForm, Post, Comments, Friends, tmpObj
from flask import Flask, render_template, redirect, url_for, request, session, flash, Response
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import string, random
from flask_login import logout_user, current_user, login_user
#from passlib.hash import sha256_crypt
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import select
import os
from sqlalchemy import update

# Set the secret key to some random bytes
app.secret_key = "96AA4DB38921EAA483F1A2A33F827"

def checkIfRepost(postTekst):
    postTekst = postTekst.replace(" ","") 
    postTekst = postTekst.strip("\n")       #Here we remove spaces, makes the text lowercase, etc
    postTekst = postTekst.lower()

    maks = Post.query.all()     #Take out all the posts

    if len(maks) != 0:
        maksverdi = maks[-1].id #Take the largest id as the max
    else:
        return False

    starten = 0
    grense = 50
    if maksverdi > grense:          #Dynamically change the values so that only the 50 newest are checked
        starten = maksverdi - grense

    postene = Post.query.all()[starten:maksverdi]

    for post in postene:
        body = post.body
        body = body.replace(" ","")
        body = body.strip("\n")
        body = body.lower()

        i = 0
        plag = 0
        prosentPlag = 0.0

        if len(body) < 10 or len(postTekst) < 10:   #If one of the bodies doesn't fit nicely into the 9/10 ratio, we use a simpler check
            if body == postTekst:
                return True
            
        else:
            prosentGrense = 0.90

            if len(body) >= len(postTekst): #This if-else duo makes sure certain letters can't be monopolized
                lengden = len(body)
            else:
                lengden = len(postTekst)

            for ordet in body:
                if i >= len(postTekst): #Break loop if body is at its end
                    break

                if postTekst[i] == ordet:       #If one letter is alike:
                    plag += 1                   #Increment the plagiarism
                    prosentPlag = plag/lengden
                    if prosentPlag >= prosentGrense:
                        return True

                i += 1
    return False

@app.route('/')
def index():
    if current_user.is_authenticated == False:
        flash("You are not authenticated")
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
        venneliste.append(Users.query.filter_by(userid=ID).first())
        postliste += Post.query.filter_by(author_id=ID).all()

    postliste += Post.query.filter_by(author_id=userid)

    postliste.sort(reverse=True, key=lambda post: post.id)
    venneliste.sort(key=lambda venn: venn.username)

    return render_template('index.html', venneliste=venneliste, postliste=postliste)


@app.route('/login', methods=['GET', 'POST'])
def login():
    #Create a WTForm for login
    form = LoginForm()
    if form.validate_on_submit():
        #Check for the username in the database to find a valid user
        #Find/Create the user object by query
        user = Users.query.filter_by(username=form.username.data).first()
        if user != None:
            #Verify inputted password with the hashed version in the database
            if hashlib.sha512(form.password.data.encode('utf-8')).hexdigest() == user.password:
                #Add to session using flask_login
                user.authenticated = True
                login_user(user, remember=False)
                return redirect(url_for('index'))
            else:
                return render_template("error.html", error="Invalid username or password!")
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

@app.route('/newFriend', methods=['GET', 'POST'])
def newFriend():
    if current_user.is_authenticated == False:
        flash("You are not authenticated")
        return redirect(url_for('login'))
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
            addResult = 0

        elif addResult != 2:
            addResult = 1
        

    return render_template('newFriend.html', form=formen, addResult=addResult)


@app.route('/createUser', methods=['GET', 'POST'])
def createUser():
    #Create WTForm for signup
    form = SignUpForm()
    print("Errors: ")
    print(form.errors)
    if form.validate_on_submit():
        if form.password.data != form.confirmPass.data:
            flash("Password fields must match")
            return render_template('createUser.html', form=form)
        if len(form.password.data) < 8 or len(form.password.data) > 50:
            flask("Password must be between 8 and 50 characters and numbers")
            return render_template('createUser.html', form=form)
        #Validate usernamee by query database to check if someone else has already claimed the username
        if validateUsername(request.form['username']) is True:
            #Generate a non-incremental user ID
            userid = generateUserID()
            #Set username and password, and has the password
            username = request.form['username']
            #password = str(sha256_crypt.hash(request.form['password']))
            password = hashlib.sha512(request.form["password"].encode('utf-8')).hexdigest()
            
            #Create Users object and add it to the database
            user = Users(username=username, password=password, userid = userid)

            db.session.add(user)
            db.session.commit()
        else:
            return render_template('error.html', error="User already exists!")
        return redirect(url_for('login'))
    for error in form.errors:
        print(error)
    return render_template('createUser.html', form=form, errors=form.errors)

@app.route('/createPost', methods=['GET', 'POST'])
def createPost():
    if current_user.is_authenticated == False:
        flash("You need to be logged in to create a post")
        return redirect(url_for('login'))
    #Create WTForm for posting
    form = PostForm()
    if form.validate_on_submit():
        f = form.photo.data
        nu = datetime.now()
        tidNu = nu.strftime("%d/%m/%Y  %H:%M:%S")
        if checkIfRepost(request.form["body"]):
            return render_template('error.html', error="Post has been deemed a repost!")
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
def viewPosts(post_id):
    if current_user.is_authenticated == False:
        flash("You need to be logged in to view posts")
        return redirect(url_for('login'))
    post = Post.query.filter_by(id=post_id).first()
    comments = Comments.query.filter_by(post_id=post_id).all()
    if comments != None:
        comments.sort(reverse=True, key=lambda post: post.id)
    return render_template('viewPost.html', post=post, comments=comments)

@app.route('/<int:post_id>/comment', methods=["GET", "POST"])
def comment(post_id):
    if current_user.is_authenticated == False:
        flash("You need to be logged in to comment on posts")
        return redirect(url_for('login'))
    form = CommentForm()
    if form.validate_on_submit():
        splitRequest = request.path.split('/')

        nu = datetime.now()
        tidNu = nu.strftime("%d/%m/%Y  %H:%M:%S")
        tmp = tmpObj.query.filter_by(userid=current_user.userid).first()
        post_id = tmp.post_id
        
        comment = Comments()
        comment.author_id = current_user.userid
        comment.author_name = current_user.username
        comment.post_id = post_id
        comment.body = request.form['body']
        comment.created = tidNu

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('viewPosts', post_id=post_id))
        
    tmpliste = tmpObj.query.filter_by(userid=current_user.userid).all()
    if len(tmpliste) > 0:
        tmpObj.query.filter_by(userid=current_user.userid).delete()
        entry = tmpObj(userid=current_user.userid, post_id=post_id)
        db.session.add(entry)
        db.session.commit()
    else:
        entry = tmpObj()
        entry.userid = current_user.userid
        entry.post_id = post_id
        db.session.add(entry)
        db.session.commit()

    return render_template('comment.html', form=form, post_id=post_id)


#Validates username by querying the database and checking if there is anyone else with that exact username (Case Sensitive)
def validateUsername(wantedName):
    validated = True
    query = Users.query.filter_by(username=wantedName).first()
    if query is None:
        return True
    else:
        return False

#Generate a user id by adding random letters together
#TODO: Include numbers in the generation as well
#TODO: FIX SO IT WORKS AS INTENDED (CAN GET SAME USER ID)
def generateUserID():
    duplicate = False
    while True:
        letters = string.ascii_lowercase
        for x in range(9):
            letters += str(x)
        result_str = ''.join(random.choice(letters) for i in range(16))

        if Users.query.filter_by(userid=str(result_str)).first() != None:
            continue

        return result_str 
