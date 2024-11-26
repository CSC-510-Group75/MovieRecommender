from movierecommender import db
from movierecommender.models import User,Post,WishlistItem, Watched, MovieLikes, Movie, Rating
import csv

db.create_all()

## Uncomment the following to add values to the Movie table if empty

# with open('movierecommender/data/movies.csv', mode='r', encoding='utf-8') as file:
#     reader = csv.reader(file)
#     next(reader)
#     for row in reader:
#         if len(row) > 1:
#             movie = Movie(id = row[0],
#                           title = row[1],
#                           genres = row[2])
#             db.session.add(movie)

# db.session.commit()