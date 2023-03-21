from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.csrf import CSRFProtect, CSRFError
import requests

API_KEY = "2f149f0e41bb5223007a312b4dd7b24b"
SEARCH_LINK = "https://api.themoviedb.org/3/search/movie"
DETAIL_LINK = "https://api.themoviedb.org/3/movie/"


# response = requests.get(LINK, params={"api_key": API_KEY, "query": "iron man"})
# data = response.json()
#
#
# print(data['results'])


db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies-collection.db'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
db.init_app(app)

Bootstrap(app)


all_movies = []


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    year = db.Column(db.String(250))
    description = db.Column(db.String(500))
    rating = db.Column(db.String(250))
    ranking = db.Column(db.String(250))
    review = db.Column(db.String(500))
    img_url = db.Column(db.String(250))

    def __repr__(self):
        return f'<Movie {self.title}'

#Setting up Form for editing movies

class Edit(FlaskForm):
    rating = FloatField(
        label="Your rating out of 10",
        validators=[NumberRange(min=0, max=10)]
    )

    review = StringField(
        label="Your Review",
    )

    submit = SubmitField(
        label="Done"
    )

class Add(FlaskForm):
    title = StringField(
        label='Movie Title',
        validators=[DataRequired()]
    )

    submit = SubmitField(
        label="Search"
    )

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    global all_movies
    with app.app_context():
        all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    # Get Id From index.html

    movie_id = request.args.get('id')

    #pull id number from data base

    movie = Movie.query.get(movie_id)

    #gets the form from Edit class from above

    form = Edit()

    #checks if the filled out form is valid
    if form.validate_on_submit():

        #Updates the data base
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        # Returns back to the home page after upload
        return redirect(url_for('home'))

    else:
        form.rating.render_kw = {"placeholder": f"Current Rating: {movie.rating}"}
        form.review.render_kw = {"placeholder": f"Current Review: {movie.review}"}
        return render_template('edit.html', form=form, movie=movie)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    to_delete = Movie.query.get(movie_id)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = Add()
    if form.validate_on_submit():
        search = form.title.data
        response = requests.get(SEARCH_LINK, params={"api_key": API_KEY, "query": search})
        data = response.json()['results']
        return render_template('select.html', options=data)


    return render_template('add.html', form=form)

@app.route('/get-data', methods=['GET', 'POST'])
def get_data():
    movie_id = request.args.get('id')
    if movie_id:
        movie_link = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        response = requests.get(movie_link)
        data = response.json()
        print(data)
        with app.app_context():
            new_movie = Movie(
                title= data['title'],
                year= data['release_date'].split("-")[0],
                description= data['overview'],
                img_url=f"https://image.tmdb.org/t/p/original{data['poster_path']}")
                # img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}"

            db.session.add(new_movie)
            db.session.commit()
        return redirect(url_for('edit'))
    return redirect(url_for('add'))





if __name__ == '__main__':
    app.run(debug=True)
