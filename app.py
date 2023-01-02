from flask import Flask, render_template, request, redirect, g, url_for, session, abort
from cs50 import SQL
from functools import wraps
from flask_session import Session
from tempfile import mkdtemp

import os
import requests
import urllib.parse

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'super secret key'
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
db = SQL("sqlite:///database.db")

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
    def decorated_func(*args, **kwargs):
        if session.get("logged_in"):
            return f(*args, **kwargs)
        else:
            return redirect("/")
    return decorated_func

@app.route('/')
@login_required
def homepage():
    positions = db.execute("SELECT * FROM positions WHERE id = ?", id)
    return render_template('homepage.html', positions=positions)


@app.route("/login", methods=["GET", "POST"])
def login():

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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (submitting the register form)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # save username and password hash in variables
        username = request.form.get("username")

        # Query database to ensure username isn't already taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("username is already taken", 400)

        # insert username and hash into database
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    username=username, password=request.form.get("password"))

        # redirect to login page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

#@app.route('/position/<int:id>')
#@login_required
#def position_details(id):
#    position_data = db.execute("SELECT * FROM positions WHERE id = ?", id)
#    return render_template('position_details.html', position=position_data)

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