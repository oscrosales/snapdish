"""
Title: SnapDish Web Application
Authors: Oscar Rosales,
Description:
Date Created: Feb 21, 2025
"""

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search.html")
def search():
    return render_template("search.html")

@app.route("/login.html")
def login():
    return render_template("login.html")

@app.route("/register.html")
def register():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug = True, host="0.0.0.0")