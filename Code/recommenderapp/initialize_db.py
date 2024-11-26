from movierecommender import db
from movierecommender.models import User,Post,WishlistItem, Watched, MovieLikes

db.create_all()