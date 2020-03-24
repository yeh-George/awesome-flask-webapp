from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from awesome_flask_webapp.extensions import db


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)



class User(db.Model, UserMixin):
    # account info
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    # user info
    name = db.Column(db.String(30))
    bio = db.Column(db.String(255))
    location = db.Column(db.String(50))
    memeber_since = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Collect(db.Model):
    id = db.Column(db.Integer, primary_key=True)

