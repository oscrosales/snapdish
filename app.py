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
import random
from gtts import gTTS
import cv2 # run pip install opencv-python
import main

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

# Fridge Model
class FridgeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_id = db.Column(db.String(50), nullable=False)
    meal_name = db.Column(db.String(200), nullable=False)
    meal_image = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref=db.backref('fridge_items', lazy=True))

@app.route('/add_to_fridge/<meal_id>/<meal_name>/<meal_image>', methods=['POST'])
@login_required
def add_to_fridge(meal_id, meal_name, meal_image):
    print(f"Adding meal_id: {meal_id}, meal_name: {meal_name}, meal_image: {meal_image}")  # Debugging line

    if FridgeItem.query.filter_by(user_id=current_user.id, meal_id=meal_id).first():
        flash('Recipe already in fridge!', 'warning')
        return redirect(url_for('recipe', id=meal_id))

    new_item = FridgeItem(user_id=current_user.id, meal_id=meal_id, meal_name=meal_name, meal_image=meal_image)
    db.session.add(new_item)

    try:
        db.session.commit()
        flash('Recipe added to fridge!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding recipe to fridge: {str(e)}', 'danger')

    return redirect(url_for('recipe', id=meal_id))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class FoodAPI():
    def __init__(self, user_input):
        self.foundMeal = False
        self.user_input = user_input

        self.meals = []

        for char in self.user_input:  # replace space with _
            if char == ' ':
                char = '_'

        self.ingredient = "filter.php?i=" + self.user_input

        self.allMeals()

    def allMeals(self):
        url = "https://www.themealdb.com/api/json/v1/1/" + self.ingredient  # searches the web with specific ingredient
        response = requests.get(url)
        data = response.json()

        self.meal_name = []
        self.meal_id = []

        if data['meals'] is not None:  # add all meals and id's in a list

            meal = data['meals'][0]

            for meal in data['meals']:
                self.meal_name.append(meal['strMeal'])
                self.meal_id.append(meal['idMeal'])

            self.foundMeal = True
        else:
            self.foundMeal = False

        return self.meal_id, self.meal_name

    def getAllMeals(self):
        if self.foundMeal:
            self.foodList = []
            if len(self.meal_name) >= 5:
                while len(self.foodList) < 5:
                    random_meal = random.choice(self.meal_name)
                    if random_meal not in self.foodList:
                        self.foodList.append(random_meal)
            else:
                for i in range(1, len(self.meal_name)):
                    some_meal = self.meal_name[i]
                    self.foodList.append(some_meal)

            return self.foodList

    def getMeal(self, foodID: str):
        url1 = "https://www.themealdb.com/api/json/v1/1/lookup.php?i=" + foodID
        response = requests.get(url1)
        data = response.json()

        meal = data['meals'][0]
        self.meal_name = meal['strMeal']
        self.meal_category = meal['strCategory']
        self.meal_area = meal['strArea']
        self.meal_instructions = meal['strInstructions']
        self.meal_image = meal['strMealThumb']

        self.meal_ingredient = []
        for i in range(1, 21):
            measure = meal.get(f'strMeasure{i}')
            ingredient = meal.get(f'strIngredient{i}')

            # Only concatenate if both are not None
            if measure and ingredient:
                ingredient_string = f"{measure} {ingredient}".strip()
                if ingredient_string:
                    self.meal_ingredient.append(ingredient_string)


def textToSpeech(food: FoodAPI, foodInstruction: str):
    if food.foundMeal == True:
        language = 'en'
        myobj = gTTS(text = str(foodInstruction), lang = language, slow = False)

        myobj.save("foodInstruction.mp3")
    else:
        print("Instructions cannot be played")


# Current users
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search = request.form["prompt"]

        food = FoodAPI(search)
        meal_ids, meal_names = food.allMeals()


        if food.foundMeal == True:
            return render_template("search.html",
                                meal_ids=meal_ids,
                                meal_names=meal_names)
        else:
            norecipe = "No recipe(s) found... Try Again!"
            return render_template("search.html", no_results = norecipe)

    return render_template("search.html")


@app.route("/capture")
def capture():
    window_name = "Capture Photo"
    photo_name = "food_picture.jpg"

    cam = cv2.VideoCapture(0)

    status, photo = cam.read()
    cam.release()

    cv2.imshow(window_name, photo)
    cv2.imwrite(photo_name, photo)

    cv2.waitKey(5000)
    cv2.destroyAllWindows()

    detection = main.show_results(photo_name, confidence_threshold=0.2)

    norecipe = "No recipe(s) found... Try Again!"
    return render_template("search.html", detection=detection)


@app.route("/recipe/<id>")
def recipe(id):
    api = FoodAPI("")

    api.getMeal(id)

    if api.foundMeal == True:
        textToSpeech(api, api.meal_instructions)

    return render_template("recipe.html",
                            name=api.meal_name,
                            image=api.meal_image,
                            category=api.meal_category,
                            ingredients=api.meal_ingredient,
                            instructions=api.meal_instructions.split(". "))

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
    saved_recipes = FridgeItem.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', saved_recipes=saved_recipes)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return render_template('logout.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")