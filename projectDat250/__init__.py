from flask import Flask, render_template, redirect, url_for, request

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

app = Flask(__name__)
#from . import db
                    # Vet ikke hva disse gjorde, men de var i veien, så jeg kommenterte de ut
#db.init_app(app)

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

import projectDat250.views