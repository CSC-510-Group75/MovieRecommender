import pandas as pd
import warnings
import os

from movierecommender import app, db
from movierecommender.models import Movie

app_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(code_dir)

warnings.filterwarnings("ignore")


def recommendForNewUser(user_rating):
    movies = Movie.query.all()
    movies_list = [[movie.id, movie.title, movie.genres] for movie in movies]
    df = pd.DataFrame(movies_list)
    df.columns = ['movieId', 'title', 'genres']

    ratings = Movie.query.all()
    ratings_list = [[rating.userId, rating.movieId, rating.rating, rating.timestamp] for rating in ratings]
    df = pd.DataFrame(ratings_list)
    df.columns = ['userId', 'movieId', 'rating', 'timestamp'] 

    user = pd.DataFrame(user_rating)
    userMovieID = movies[movies["title"].isin(user["title"])]
    userRatings = pd.merge(userMovieID, user)

    moviesGenreFilled = movies.copy(deep=True)
    copyOfMovies = movies.copy(deep=True)
    for index, row in copyOfMovies.iterrows():
        copyOfMovies.at[index, "genres"] = row["genres"].split("|")
    for index, row in copyOfMovies.iterrows():
        for genre in row["genres"]:
            moviesGenreFilled.at[index, genre] = 1
    moviesGenreFilled = moviesGenreFilled.fillna(0)

    userGenre = moviesGenreFilled[moviesGenreFilled.movieId.isin(userRatings.movieId)]
    userGenre.drop(["movieId", "title", "genres"], axis=1, inplace=True)
    userProfile = userGenre.T.dot(userRatings.rating.to_numpy())
    moviesGenreFilled.set_index(moviesGenreFilled.movieId)
    moviesGenreFilled.drop(["movieId", "title", "genres"], axis=1, inplace=True)

    recommendations = (moviesGenreFilled.dot(userProfile)) / userProfile.sum()
    joinMoviesAndRecommendations = movies.copy(deep=True)
    joinMoviesAndRecommendations["recommended"] = recommendations
    joinMoviesAndRecommendations.sort_values(
        by="recommended", ascending=False, inplace=True
    )
    #print("returning value " ,[x for x in joinMoviesAndRecommendations["title"]][:201]) #~
    return [x for x in joinMoviesAndRecommendations["title"]][:201]
