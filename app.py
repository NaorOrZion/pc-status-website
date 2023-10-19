"""
Author: Naor Or-Zion
Unit:   Basmach-Alpha
Date:   19.10.2023

Brief: The 'app.py' is the main navigation file for the website
"""

from flask import Flask, render_template

app = Flask(__name__)
app.config["SECRET_KEY"] = "pc-status"


@app.route("/")
def home():
    return render_template(
        "home.html",
    )


if __name__ == "__main__":
    app.run(debug=True)
