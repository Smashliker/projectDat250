from flask import Flask, render_template, redirect, url_for, request

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import flask_login
from flask_login import UserMixin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["3/second"]
)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("projectDat250/database.db")
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('./schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

init_app(app)
bcrypt = Bcrypt(app)
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
from wtforms.validators import DataRequired, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed

#NumberRange(min=0, max=10)]

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class FriendForm(FlaskForm):
    friendName = StringField('Friend name', validators=[DataRequired()])
    submit = SubmitField('Add Friend')
    
class SignUpForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    confirmPass = PasswordField('confirmpass', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body')
    photo = FileField(validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
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
    post_id = db.Column(db.String)
    author_name = db.Column(db.String)
    body = db.Column(db.String)
    created = db.Column(db.String)

class Friends(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String)
    friendid = db.Column(db.String)


import projectDat250.views

