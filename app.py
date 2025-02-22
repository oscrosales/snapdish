"""
Title: SnapDish Web Application
Authors: Oscar Rosales,
Description:
Date Created: Feb 21, 2025
"""

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flaskuser:flaskpass@localhost/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-secret-key'  # Change this in production

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

class FoodAPI():
    def __init__(self, user_input):
        self.foundMeal = False
        self.user_input = user_input

        self.meals = []

        for char in self.user_input: # replace space with _
            if char == ' ':
                char = '_'

        self.ingredient = "filter.php?i=" + self.user_input

    def getMeals(self):
        url = "https://www.themealdb.com/api/json/v1/1/" + self.ingredient # searches the web with specific ingredient
        response = requests.get(url)
        data = response.json()

        if data["meals"] != None:
            meal = data['meals'][0]

            for meal in data["meals"]:
                self.meals.append(meal)

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search = request.form["prompt"]

        api = FoodAPI(search)

        return render_template("search.html", results=api.getMeals())

    return render_template("search.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome, {current_user.username}! <a href='/logout'>Logout</a>"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = True, host="0.0.0.0")