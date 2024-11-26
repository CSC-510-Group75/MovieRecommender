
from datetime import datetime
from movierecommender import db , login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}','{self.movieratings}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
  
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.content}')"
    
#Group49
class WishlistItem(db.Model):
    __tablename__ = 'wishlist_item'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

#Group 49
class Watched(db.Model):
    __tablename__ = 'watched_item'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genres =  db.Column(db.String(100), nullable=False)


class MovieLikes(db.Model):
    __tablename__ = 'movie_likes'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String(100), unique=True, nullable=False)
    like_count = db.Column(db.Integer, default=0)


