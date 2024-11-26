from flask import render_template,url_for,flash,redirect,jsonify,request
from flask_cors import CORS, cross_origin
from movierecommender import app,db, bcrypt
from movierecommender.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from movierecommender.models import User, Post, WishlistItem, Watched, MovieLikes, Movie
import json
import sys
import csv
import time
import requests
from movierecommender.prediction_scripts.item_based import recommendForNewUser
from movierecommender.search import Search
import random
from sqlalchemy import func

CORS(app, resources={r"/*": {"origins": "*"}})
 
# Replace 'YOUR_API_KEY' with your actual OMDB API key
OMDB_API_KEY = 'b726fa05'

with open('movierecommender/api_key.txt', 'r') as file: # Trailer API
    api_key = file.read().strip()



def get_movie_info(title):
    index=len(title)-6
    url = f"http://www.omdbapi.com/?t={title[0:index]}&apikey={OMDB_API_KEY}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        res=response.json()
        if(res['Response'] == "True"):
            return res
        else:  
            return { 'Title': title, 'imdbRating':"N/A", 'Genre':'N/A',"Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}
    else:
        return  { 'Title': title, 'imdbRating':"N/A",'Genre':'N/A', "Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}


def get_movie_info1(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        res=response.json()
        if(res['Response'] == "True"):
            return res
        else:  
            return { 'Title': title, 'imdbRating':"N/A", 'Genre':'N/A',"Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}
    else:
        return  { 'Title': title, 'imdbRating':"N/A",'Genre':'N/A', "Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}



@app.route("/home")
def landing_page():
    return render_template("landing_page.html")

@app.route("/", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('landing_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('landing_page'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('register'))
@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

    


@app.route("/predict", methods=["POST"])
def predict():
    data = json.loads(request.data)  # contains movies from the user
    print("data ",data) #~
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        training_data.append(movie_with_rating)
    recommendations = recommendForNewUser(training_data)
    recommendations = recommendations[:3] # Top 5 recommended
    print("recommendations Top 5", recommendations) #~
    for movie in recommendations:
        movie_info = get_movie_info(movie)
        #print("movie_info", movie_info) #~

        if(movie_info.get('imdbID')): # IMDB ID
            imdb_id = movie_info['imdbID'] #~
            #print("IMDB id = ", imdb_id)
            url = f'https://api.themoviedb.org/3/find/{imdb_id}?external_source=imdb_id&api_key={api_key}'
            resp = requests.get(url)
            if resp.status_code == 200:
                res1=resp.json()
                #print('res1', res1)

                if(res1["movie_results"]):
                    movie_id = res1["movie_results"][0]['id']
                    print('movie id', movie_id)
                    url2 = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?language=en-US&api_key={api_key}'
                    res_vid = requests.get(url2)
                    if res_vid.status_code == 200:
                        res_vid=res_vid.json()
                        #print("res_vid",res_vid)
                        if(res_vid['results']):
                            url_vid = f"https://www.youtube.com/watch?v={res_vid['results'][0]['key']}"
                            #print('url_vid_________________',url_vid)
                        else:
                            #print('empty video')
                            url_vid = None
                    else:
                        url_vid = None
                else:
                    movie_id = None
                    print('Empty list')
                    url_vid=None
            else:
                url_vid = None
                
        else:
            imdb_id = None #~
            url_vid = None
        #print(movie_info['imdbRating']) 
        if movie_info:
            movie_with_rating[movie+"-r"]=movie_info['imdbRating']
            movie_with_rating[movie+"-g"]=movie_info['Genre']
            movie_with_rating[movie+"-p"]=movie_info['Poster']
            movie_with_rating[movie+"-u"]=url_vid

    resp = {"recommendations": recommendations, "rating":movie_with_rating}
    return resp

@app.route("/search", methods=['GET','POST'])
def search():
    term = request.form["q"]
    print("term= ", term) #~
    search = Search()
    filtered_dict = search.resultsTop5(term)
    resp = jsonify(filtered_dict)
    resp.status_code = 200
    return resp


def get_movie_by_title(title):
    # Simulate a movie database lookup
    #print(title)
    index=len(title)-6
    url = f"http://www.omdbapi.com/?t={title[0:index]}&apikey={OMDB_API_KEY}"
    #print(url)
    response = requests.get(url)
    res=response.json()
    #print(res)
    return res
    
@app.route('/movie/<string:title>')
def movie_detail(title):
    # Fetch the movie details based on the title
    movie = get_movie_by_title(title)
    print(movie)
    if movie["Response"]=='False':
        return "Movie not found", 404 
    else:
        return render_template('movies_details.html', movie=movie)

if __name__ == '__main__':
    app.run(debug=True, port=5001)


@app.route("/feedback", methods=["POST"])
def feedback():
    data = json.loads(request.data)
    stri=""
    with open(f"experiment_results/feedback_{int(time.time())}.csv", "w") as f:
        for key in data.keys():
            f.write(f"{key} - {data[key]}\n")
            stri+=key+":"+data[key]+" "
            

    post = Post(title="movieratings", content=stri, author=current_user)
    db.session.add(post)
    db.session.commit()
    print(data)
    return data
@app.route("/movie")
def movie():
    posts=Post.query.all()
    return render_template("movie.html",posts=posts)

@app.route("/success")
def success():
    return render_template("success.html")


@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    movie_titles = [movie.title for movie in movies]

    return jsonify(movie_titles)

@app.route('/api/movie_details', methods=['GET'])
def movie_details():
    title = request.args.get('title')
    index=len(title)-6
    url = f"http://www.omdbapi.com/?t={title[0:index]}&apikey={OMDB_API_KEY}"
    #print(url)
    response = requests.get(url)
    res=response.json()
    #if (res["Response"] == "Success"):
    details = {
        "title": title,
        "poster": res["Poster"],
        "genre": res["Genre"],
        "director": res["Director"],
        "rating": res["imdbRating"]
        }
    # else:
    #     details={
    #         "title":title,
    #         "poster":url_for('static', filename='image.jpeg'),
    #         "genre":"N/A",
    #         "director":"N/A",
    #         "rating":"N/A"
    #     }
    return jsonify(details)

@app.route("/api/add_to_wishlist/<string:title>", methods=["POST"])
def add_to_wishlist(title):
    if not current_user.is_authenticated:
        return jsonify({"error": "Please log in to add items to your wishlist."}), 401

    new_wishlist_item = WishlistItem(title=title, user_id=current_user.id)

    try:
        db.session.add(new_wishlist_item)
        db.session.commit()
        return jsonify({"success": True, "message": "Movie added to your wishlist!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Failed to add movie to wishlist."}), 500
    
@app.route("/api/add_to_watched/<string:title>", methods=["POST"])
def add_to_watched(title):
    if not current_user.is_authenticated:
        return jsonify({"error": "Please log in to add items to your wishlist."}), 401

    new_wishlist_item = Watched(title=title, user_id=current_user.id)

    try:
        db.session.add(new_wishlist_item)
        db.session.commit()
        return jsonify({"success": True, "message": "Movie added to your watched history!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Failed to add movie to watched history."}), 500
    
@app.route("/wishlistItems")
def wishlistItems():
    wishlist_movies = (
        db.session.query(WishlistItem.title, func.min(WishlistItem.added_on).label('added_on'))
        .filter_by(user_id=current_user.id)
        .group_by(WishlistItem.title)
        .all()
    )

    # Convert the results into a list of dictionaries for easier access in the template
    movies_list1 = [
        {**get_movie_info1(title), 'title': title, 'added_on': added_on}
        for title, added_on in wishlist_movies
    ]
    
    return render_template('wishlist.html', wishlist_movies=movies_list1)

@app.route("/watched")
def watched():
    watched_movies = (
        db.session.query(Watched.title, func.min(Watched.added_on).label('added_on'))
        .filter_by(user_id=current_user.id)
        .group_by(Watched.title)
        .all()
    )
    
    # Convert the results into a list of dictionaries for easier access in the template
    movies_list2 = [
        {**get_movie_info1(title), 'title': title, 'added_on': added_on}
        for title, added_on in watched_movies
    ]
    print(movies_list2)
    
    return render_template('watched.html', watched_movies=movies_list2)

#Group 49 new

# like_counts = {}

# @app.route('/like_movie', methods=['POST'])
# def like_movie():
#     data = request.get_json()
#     movie_title = data.get('movie_title')
#     user_id = current_user.id
#     print("hello")
#     # Update the like count in the dictionary (mock database)
#     if movie_title:
#         like_counts[movie_title] = like_counts.get(movie_title, 0) + 1
#         new_like_count = like_counts[movie_title]
#         return jsonify({'new_like_count': new_like_count}), 200
#     return jsonify({'error': 'Movie title is missing'}), 400


@app.route('/like_movie', methods=['POST'])
def like_movie():
    data = request.get_json()
    print(data)
    movie_title = data.get('movie_title')  
    
    if movie_title is not None:  
        like_record = MovieLikes.query.filter_by(movie_id=movie_title).first()
        print(movie_title)
        print(like_record)
        if like_record:
            like_record.like_count += 1
        else:
            like_record = MovieLikes(movie_id=movie_title, like_count=1)
            
            db.session.add(like_record)

        
        
        db.session.commit()  # Commit the changes to the database
        
        return jsonify({'new_like_count': like_record.like_count}), 200
    
    return jsonify({'error': 'Movie ID is missing'}), 400

if __name__ == "__main__":
    app.run(debug=True)


