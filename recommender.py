# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

import datetime
from flask import Flask, render_template, request
from flask_user import login_required, UserManager, current_user

from models import db, User, Movie, MovieGenre, Link, Tag, Rating
from read_data import check_and_read_data

# import sleep from python
from time import sleep

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

#collaborative filtering 

from models import db, User, Movie, MovieGenre, Link, Tag, Rating
from read_data import check_and_read_data
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity



# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Movie Recommender"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

    # make sure we redirect to home view, not /
    # (otherwise paths for registering, login and logout will not work on the server)
    USER_AFTER_LOGIN_ENDPOINT = 'home_page'
    USER_AFTER_LOGOUT_ENDPOINT = 'home_page'
    USER_AFTER_REGISTER_ENDPOINT = 'home_page'


def user_based_collaborative_filtering(user_id):
    # Retrieve user ratings
    user_ratings = Rating.query.filter_by(userId=user_id).all()

    # Get all users who have also rated the same movies
    similar_users = set()
    for rating in user_ratings:
        movie_ratings = Rating.query.filter_by(movieId=rating.movieId).all()
        for other_rating in movie_ratings:
            if other_rating.userId != user_id:
                similar_users.add(other_rating.userId)

    # Calculate similarity scores between the specified user and similar users
    similarity_scores = {}
    for other_user_id in similar_users:
        other_user_ratings = Rating.query.filter_by(userId=other_user_id).all()

        common_movies = set(rating.movieId for rating in user_ratings).intersection(
            rating.movieId for rating in other_user_ratings
        )

        if common_movies:
            user_vector = [rating.rating for rating in user_ratings if rating.movieId in common_movies]
            other_user_vector = [rating.rating for rating in other_user_ratings if rating.movieId in common_movies]

            # Use cosine similarity
            similarity_score = calculate_cosine_similarity(user_vector, other_user_vector)

            similarity_scores[other_user_id] = similarity_score

    # Sort users by similarity score in descending order
    sorted_users = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    # Get top N similar users
    top_users = sorted_users[:5]  # Adjust N as needed

    # Return the top similar users
    return top_users

def calculate_cosine_similarity(vector1, vector2):
    # Calculate the cosine similarity between two vectors
    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    magnitude1 = sum(a ** 2 for a in vector1) ** 0.5
    magnitude2 = sum(b ** 2 for b in vector2) ** 0.5

    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    similarity_score = dot_product / (magnitude1 * magnitude2)
    return similarity_score

def collaborative_filtering_recommendations(user_id):
    # Get top similar users
    similar_users = user_based_collaborative_filtering(user_id)

    # Extract movie recommendations from similar users
    recommended_movie_ids = set()
    for similar_user_id, _ in similar_users:
        similar_user_ratings = Rating.query.filter_by(userId=similar_user_id).all()
        for rating in similar_user_ratings:
            if rating.movieId not in [r.movieId for r in Rating.query.filter_by(userId=user_id).all()]:
                recommended_movie_ids.add(rating.movieId)

    # Get movie details based on recommended IDs
    recommended_movies = Movie.query.filter(Movie.id.in_(recommended_movie_ids)).all()

    return recommended_movies



# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = UserManager(app, db, User)  # initialize Flask-User management


@app.cli.command('initdb')
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')
    # Collaborative Filtering
    #user_based_collaborative_filtering()  # Add this line to call the collaborative filtering function


# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")


# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies')
@login_required  # User must be authenticated
def movies_page():
    # String-based templates

    # First 30 movies
    movies = Movie.query.limit(30).all()

    # Collaborative Filtering Recommendations
    #collaborative_filtering_recommendations = user_based_collaborative_filtering(current_user.id)


    # only Romance movies
    # movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()

    # only Romance AND Horror movies
    # movies = Movie.query\
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Romance')) \
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
    #     .limit(10).all()

    return render_template("movies.html", movies=movies)


@app.route('/rate', methods=['POST'])
@login_required  # User must be authenticated
def rate():
    movieId = request.form.get('movieid')
    rating = int(request.form.get('rating'))
    rating_num = rating
    userId = current_user.id
    dt_object = datetime.datetime.now()
    if Rating.query.filter_by(userId=userId, movieId=movieId).count() > 0:
        rating = Rating.query.filter_by(userId=userId, movieId=movieId).first()
        rating.rating = rating_num
        rating.timestamp = dt_object
        db.session.commit()
    else:
        rating = Rating(userId=userId, movieId=movieId, rating=rating, timestamp=dt_object)
        db.session.add(rating)
        db.session.commit()
    print("Rate {} for {} by {}".format(rating, movieId, userId))
    return render_template("rated.html", rating=rating_num)


# Route to display collaborative filtering recommendations for a specific user
@app.route('/recommendations', methods=['GET'])
@login_required
def display_recommendations():

    print("Reached display_recommendations")  # Debugging statement

    # Get user_id from the query parameters
    user_id = int(request.args.get('user_id', 1))  # Default to 1 if not provided

    # Get collaborative filtering recommendations for the specified user
    recommendations = collaborative_filtering_recommendations(user_id)

    # Render the recommendations template with the recommended movies
    return render_template("recommendations.html", recommendations=recommendations)



# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)



