from flask import Flask, render_template, request, redirect, g, url_for, session
from cs50 import SQL
from functools import wraps
from flask_session import Session
import os
import requests
import urllib.parse

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQL("sqlite:///finance.db")

Session(app)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def homepage():
    positions = 0
    #return render_template('homepage.html', positions=positions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not (rows[0]["password"] ==  request.form.get("password")):
            return apology("invalid username and/or password", 400)

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route('/position/<int:id>')
@login_required
def position_details(id):
    position_data = db.execute("SELECT * FROM positions WHERE id = ?", id)
    return render_template('position_details.html', position=position_data)

@app.route('/apply/<int:id>')
@login_required
def apply(id):
    position_data = db.execute("SELECT * FROM positions WHERE id = ?", id)
    return render_template('apply.html', position_data= position_data)

@app.route('/apply/<int:id>', methods=['POST'])
@login_required
def submit_application(id):
    resume = request.form("resume")
    misc = request.form("misc")
    db.execute("INSERT INTO data (user_id, positions_id, resume, misc) VALUES (?, ?, ?, ?)", session["user_id"], id, resume, misc)
    return render_template('success.html', position_id=id)

@app.route('/applied')
@login_required
def applied():
    applied_positions = db.execute("SELECT * FROM data WHERE user_id = ?", session["user_id"])
    return render_template('applied.html', positions=applied_positions)