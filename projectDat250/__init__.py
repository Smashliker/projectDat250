from flask import Flask, render_template, redirect, url_for, request
from flask_bcrypt import Bcrypt
app = Flask(__name__)
from . import db

import projectDat250.views

db.init_app(app)

bcrypt = Bcrypt(app)

