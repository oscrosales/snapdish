"""
Title: SnapDish Web Application
Authors: Oscar Rosales,
Description:
Date Created: Feb 21, 2025
"""

from flask import Flask, render_template, request
import requests

app = Flask(__name__)

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



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search = request.form["prompt"]

        api = FoodAPI(search)

        return render_template("search.html", results=api.getMeals())

    return render_template("search.html")



@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug = True, host="0.0.0.0")