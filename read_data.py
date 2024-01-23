import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, Link, Tag, Rating, User
import datetime
import random
import string

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if database is empty
    if Movie.query.count() == 0:
        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)
                        genres = row[2].split('|')  # genres is a list of genres
                        for genre in genres:  # add each genre to the movie_genre table
                            movie_genre = MovieGenre(movieId=id, genre=genre)
                            db.session.add(movie_genre)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")
    
    # check if we have links in the database
    # read data if database is empty
    if Link.query.count() == 0:
        # read links from csv
        with open('data/links.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        movieId = row[0]
                        imdbId = row[1]
                        tmdbId = row[2]
                        movielensLink = "https://movielens.org/movies/" + movieId
                        imdbLink = "https://www.imdb.com/title/tt" + imdbId
                        tmdbLink = "https://www.themoviedb.org/movie/" + tmdbId
                        link = Link(movieId=movieId, imdbId=imdbId, tmdbId=tmdbId, movielensLink=movielensLink, imdbLink=imdbLink, tmbLink=tmdbLink)
                        db.session.add(link)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate link for movie with ID: " + movieId)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " links read")
    
    # check if we have tags in the database
    # read data if database is empty
    if Tag.query.count() == 0:
        # read tags from csv
        with open('data/tags.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        userId = row[0]
                        movieId = row[1]
                        tag = row[2]
                        timestamp = row[3]
                        dt_object = datetime.datetime.fromtimestamp(int(timestamp))
                        tag = Tag(userId=userId, movieId=movieId, tag=tag, timestamp=dt_object)
                        db.session.add(tag)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate tag for movie with ID: " + movieId)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " tags read")
    
    # check if we have ratings in the database
    # read data if database is empty
    if Rating.query.count() == 0:
        # read ratings from csv
        with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        userId = row[0]
                        movieId = row[1]
                        rating = row[2]
                        timestamp = row[3]
                        dt_object = datetime.datetime.fromtimestamp(int(timestamp))
                        rating = Rating(userId=userId, movieId=movieId, rating=rating, timestamp=dt_object)
                        db.session.add(rating)
                        db.session.commit()  # save data to database
                        
                        # add user to users table
                        if User.query.filter_by(id=userId).count() == 0:
                            username = generate_random_username()
                            userpw = generate_random_password()
                            user = User(id=userId, username=username, password=userpw)
                            db.session.add(user)
                            db.session.commit()
                        
                    except IntegrityError:
                        print("Ignoring duplicate rating for movie with ID: " + movieId)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " ratings read")


def generate_random_username(length=8):
    username = ''.join(random.choices(string.ascii_lowercase, k=length))
    return username

def generate_random_password(length=12):
    password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))
    return password