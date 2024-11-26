import pandas as pd

# from app import app
from movierecommender import app, db
from movierecommender.models import Movie

from flask import jsonify, request, render_template
import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(code_dir)


class Search:

    df = pd.read_csv(code_dir + "/movierecommender/data/movies.csv")
    
    movies = Movie.query.all()
    movies_list = [[movie.id, movie.title, movie.genres] for movie in movies]
    df = pd.DataFrame(movies_list)
    df.columns = ['movieId', 'title', 'genres'] 

    def __init__(self):
        pass

    def startsWith(self, word):
        n = len(word)
        res = []
        word = word.lower()
        for x in self.df["title"]:
            curr = x.lower()
            if curr[:n] == word:
                res.append(x)
        return res

    def anywhere(self, word, visitedWords):
        res = []
        word = word.lower()
        for x in self.df["title"]:
            if x not in visitedWords:
                curr = x.lower()
                if word in curr:
                    res.append(x)
        return res

    def results(self, word):
        startsWith = self.startsWith(word)
        visitedWords = set()
        for x in startsWith:
            visitedWords.add(x)
        anywhere = self.anywhere(word, visitedWords)
        startsWith.extend(anywhere)
        return startsWith

    def resultsTop5(self, word):
        
        return self.results(word)[:5]


if __name__ == "__main__":
    app.run()
