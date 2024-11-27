from datetime import datetime
from movierecommender import db , login_manager
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    
    posts = db.relationship('Post', backref='author', lazy=True)
    two_factor_secret = db.Column(db.String(16), nullable=True, default=None)
    two_factor_enabled = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
  
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.content}')"
    
#Group49
class WishlistItem(db.Model):
    __tablename__ = 'wishlist_item'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"WishlistItem('{self.title}', '{self.user_id}')"
        
        
class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('wishlist', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('wishlisted_by', lazy=True))
    
    def __repr__(self):
        return f'<Wishlist {self.id} - User {self.user_id} - Movie {self.movie_id}>'

#Group 49
class Watched(db.Model):
    __tablename__ = 'watched'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='watched')

# #Group 49 new
# class Movie(db.Model):
#     __tablename__ = 'movies'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     like_count = db.Column(db.Integer, default=0)  # Store the count of likes

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    like_count = db.Column(db.Integer, default=0)

class MovieLikes(db.Model):
    __tablename__ = 'movie_likes'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    like_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"MovieLikes('{self.movie_id}', '{self.like_count}')"
