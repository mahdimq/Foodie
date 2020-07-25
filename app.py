import os
from flask import Flask, render_template, redirect, request, g, flash, session, jsonify
from models import db, connect_db, User, Recipe, Favorite
# from secret import API_KEY
from forms import SignupForm, LoginForm, EditUserForm, RecipeForm
from sqlalchemy.exc import IntegrityError
import requests

# ##### TEMP DATA ########
from users import recipe, mealtypes, diets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///foodie'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secret_recipe'

connect_db(app)

# request.args -> gets query string for get route
# request.params -> gets form data for post route

# ###################### API INFORMATION ######################

# SEARCH BY INGREDIENT (can be separated by comma)
recipe_url = "/findByIngredients"

# GET RECIPE INFORMATION (ingredients, nutrition, diet and allergen information)
info_url = "/{id}/information"

# GET RANDOM RECIPES - NUMBER PARAM returns amount of recipes
rand_url = "/random"

# GET A SHOPPING LIST for a given user
shop_url = "https://api.spoonacular.com/mealplanner/{username}/shopping-list"


# #################### SPOONACULAR BASE URL ########################
BASE_URL = "https://api.spoonacular.com/recipes"

# ###################### SPOONACULAR API KEY #######################
API_KEY = "db254b5cd61744d39a2deebd9c361444"

# ########################## USER SESSION ##########################
CURR_USER = "user_id"


# #################### TO DO BEFORE REQUEST ####################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])

    else:
        g.user = None

# ############### SIGN UP FORM ################

@ app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    Handles user signup.
    GET Displays signup form
    POST Creates/Adds new user to DB and redirects home
    """

    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        image = form.img_url.data or User.img_url.default.arg

        new_user = User.register(username, password, email, image)
        db.session.add(new_user)

        # ######## NEED TO FIX ERROR HANDLING ###########
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.username.errors.append("Username taken, please pick another")
            return render_template("/users/signup.html", form=form)

        # ADD USER TO SESSION
        session[CURR_USER] = new_user.id
        flash("Thank you for registering", "warning")
        # flash("Thank you for registering", "warning")
        return redirect(f"/users/{new_user.id}")
        #     db.session.commit()

        ##################################################

        # ADD USER TO SESSION
        # session[CURR_USER] = new_user.id
        # flash("Thank you for registering", "warning")

        # return redirect(f"/users/{new_user.id}")

    return render_template('/users/signup.html', form=form)


# #################### LOGIN ROUTE ######################

@ app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    if CURR_USER in session:
        flash("You're already signed in!", 'danger')
        return redirect(f"/users/{session[CURR_USER]}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session[CURR_USER] = user.id
            flash(f"Welcome back {user.username}!", "success")
            # return redirect(f"/users/{user.id}")
            return redirect("/")
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template("users/login.html", form=form)


# # ################## HOME PAGE BASIC ###################

@app.route("/")
def homepage():
    """Show home page with or without auth
    auto populate it with random recipes"""
    res = requests.get(f"{BASE_URL}/random", params ={ "apiKey": API_KEY, "number": 9 })

    data = res.json()
    # print("###########################")
    # print(data)
    # print("###########################")

    # if len(data['recipes']) == 0:
    #     return (jsonify(data=data), 200)

    # return (jsonify(data=data), 200)

    # temp recipe population
    r_title = [r for r in recipe]
    diet = [d for d in diets]
    return render_template("index.html", title=r_title, diets=diet)


# ################## USER DETAILS BASIC ###################

@app.route("/users/<int:id>")
def show_user(id):
    """Redirect to users page"""

    if CURR_USER not in session or id != session[CURR_USER]:
        flash("You must be logged in to view this page", "danger")
        return redirect("/login")

    user = User.query.get_or_404(id)
    return render_template("/users/users.html", user=user)


# ========= NEED TO USE PATCH METHOD =========
@app.route("/users/<int:id>/update", methods=["GET", "POST"])
def update_user(id):
    """Show user update form and redirect to users page"""

    user = User.query.get(id)

    if id != session[CURR_USER] or "user_id" not in session:
        flash("You do not have permission to do delete this user!", "primary")
        return redirect(f"/users/{session[CURR_USER]}")

    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.img_url = form.img_url.data

        db.session.commit()
        flash('Changes successfully made to account', 'info')
        return redirect(f'/users/{id}')
    try:
        return render_template("/users/update.html", form=form, user=user)
    except:
        return ('', 403)


# #################### DELETE USER ROUTE ####################

# ============= NEED TO USE DELETE METHOD =============
@app.route("/users/<int:id>/delete", methods=["POST"])
def delete_user(id):
    """Delete user."""

    # Check if user is authorized
    if id != session[CURR_USER] or "user_id" not in session:
        flash("You do not have permission to do delete this user!", "primary")
        return redirect(f"/users/{session[CURR_USER]}")

    # Delete user from database
    else:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        # remove from session
        session.pop(CURR_USER)
        flash(f"{g.user.username}'s account has been deleted!", "info")
        return redirect("/")

# ####################### SHOW RECIPES ######################

@app.route("/recipe")
def show_recipe():
    """Show recipe details"""


    return render_template("recipe.html")

# ####################### LOGOUT ROUTE ######################

@ app.route('/logout')
def logout():
    """Handle logout of user."""
    session.pop(CURR_USER)
    flash("You have been logged out!", "success")
    return redirect("/")

# ##################### ERROR 404 PAGE ######################

@app.errorhandler(404)
def page_not_found(error):
    """Show 404 ERROR page if page NOT FOUND"""

    return render_template("error.html"), 404

