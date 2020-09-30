from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)
from . import db

import projectDat250.views

db.init_app(app)

