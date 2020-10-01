from flask import Flask, render_template, redirect, url_for, request

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import flask_login
from flask_login import UserMixin

from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/ove/repos/uis/projectDat250/projectDat250/database.db'


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

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Log In')


import projectDat250.views

