from flask_sqlalchemy import SQLAlchemy
import bcrypt
import random, string
from projectDat250.__init__ import app

db = SQLAlchemy(app)

class User(db.Model):
    userid = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)


    @userid.setter
    def _set_userid(self, length=15):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        self.userid = result_str


    @_password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.hashpw(plaintext, bcrypt.gensalt())

    @login_manager.user_loader
    def user_loader(self, userid):
        return User.query.get(user_id)