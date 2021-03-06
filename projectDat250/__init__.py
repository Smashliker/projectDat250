from flask import Flask, render_template, redirect, url_for, request
import os

import click
from flask import current_app, g, session
from flask.cli import with_appcontext
import flask_login
from flask_login import UserMixin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta

import psycopg2
import psycopg2.extras

app = Flask(__name__)

DATABASE = os.environ['DATABASE_URL']

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)


limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["3/second"]
)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

from flask_sqlalchemy import SQLAlchemy
import bcrypt
import random, string

db = SQLAlchemy(app)

class Users(UserMixin, db.Model):
    userid = db.Column(db.String, primary_key=True)
    __tablename__ = 'users'
    username = db.Column(db.String)
    password = db.Column(db.String)

    def get_id(self):
        return self.userid

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return Users.query.get(user_id)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length, NoneOf, Regexp
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class FriendForm(FlaskForm):
    friendName = StringField('Friend name', validators=[DataRequired()])
    submit = SubmitField('Add Friend')

weakPasswords = ["12345678", "PasswordPassword", "password123", "passwordpassword", "87654321"]
class SignUpForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[
        DataRequired(), 
        EqualTo('confirmPass', message='Passwords must match'),
        Length(min=8, max=50, message='Password is too short'),
        NoneOf(weakPasswords, message='Weak password detected'),
        Regexp("\d.*[A-Z]|[A-Z].*\d", message='Password must contain at least 1 capital letter and 1 number')
        ])
    confirmPass = PasswordField("Confirm Password")
    submit = SubmitField('Register')

class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[
        Length(min=0, max=500, message="Post body is too large")])
    photo = FileField(validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only (jpg, jpeg, or png!')])
    submit = SubmitField('Create Post')

class CommentForm(FlaskForm):
    body = StringField('body', validators=[DataRequired()])
    submit = SubmitField('Comment on post')

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    created = db.Column(db.String)
    author_id = db.Column(db.String)
    author_name = db.Column(db.String)
    image_path = db.Column(db.String)

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.String)
    post_id = db.Column(db.Integer)
    author_name = db.Column(db.String)
    body = db.Column(db.String)
    created = db.Column(db.String)

class Friends(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String)
    friendid = db.Column(db.String)

class tmpObj(db.Model):
    __tablename__ = "tmp"
    userid = db.Column(db.String, primary_key=True)
    post_id = db.Column(db.Integer)

import projectDat250.views

