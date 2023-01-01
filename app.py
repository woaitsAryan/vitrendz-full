from flask import Flask, render_template, request, redirect, g, url_for
import cs50
from functools import wraps


app = Flask(__name__)

db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

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
    positions = database.get_open_positions()
    return render_template('homepage.html', positions=positions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/position/<int:id>')
def position_details(id):
    position = db.execute("SELECT * FROM positions")
    return render_template('position_details.html', position=position)

@app.route('/apply/<int:id>')
def apply(id):
    return render_template('apply.html', position_id=id)

@app.route('/apply/<int:id>', methods=['POST'])
def submit_application(id):
    form_data = request.form
    if database.validate_application(form_data):
        database.submit_application(id, form_data)
        return render_template('confirmation.html', position_id=id)
    else:
        return render_template('apply.html', position_id=id, error='Invalid form data')

@app.route('/applied')
def applied():
    applied_positions = database.get_applied_positions()
    return render_template('applied.html', positions=applied_positions)
