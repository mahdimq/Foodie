import os
from flask import Flask, render_template, redirect, request, g, flash, session, jsonify
from models import db, connect_db, User, Recipe, Favorite
from secret import key, key2
from forms import SignupForm, LoginForm, EditUserForm, RecipeForm
from sqlalchemy.exc import IntegrityError
import requests

# ##### TEMP DATA ########
from users import recipe, diets, results, info

# ######################

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///foodie'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secret_recipe'

connect_db(app)

# request.args -> gets query string for get route
# request.params -> gets form data for post route

# #################### SPOONACULAR API INFO ########################
BASE_URL = "https://api.spoonacular.com/recipes"
API_KEY = key2
# ########################## USER SESSION ##########################
CURR_USER = "user_id"

# #################### EDAMAM API INFO ####################
# APP_ID = "1bfa73e6"
# APP_KEY = "59669656fdf109339b840b29caad7d34"
# BASE_URL = "https://api.edamam.com/search"
# #########################################################

#################### HELPERS ####################

cuisines = ['african', 'chinese', 'japanese', 'korean', 'vietnamese', 'thai', 'indian', 'british', 'irish', 'french', 'italian', 'mexican','spanish', 'middle eastern', 'jewish', 'american', 'cajun', 'southern', 'greek', 'german', 'nordic', 'eastern european', 'caribbean', 'latin american']
diets = ['pescetarian', 'lacto vegetarian','ovo vegetarian', 'vegan', 'vegetarian']

# ##############################################



# #################### TO DO BEFORE REQUEST ####################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])

    else:
        g.user = None

    g.cuisines = [cuisine for cuisine in cuisines]
    g.diets = [diet for diet in diets]

# @app.after_request
# def add_header(response):
#     response.headers['Accept-Encoding'] = 'gzip'
#     return response

#==============================================================
# USER ROUTES
# =============================================================

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


# ####################### LOGOUT ROUTE ######################

@app.route('/logout')
def logout():
    """Handle logout of user."""
    session.pop(CURR_USER)
    flash("You have been logged out!", "success")
    return redirect("/")


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


# ################### SHOW USER DETAILS ####################

@app.route("/users/<int:id>")
def show_user(id):
    """Redirect to users page"""

    if CURR_USER not in session or id != session[CURR_USER]:
        flash("You must be logged in to view this page", "danger")
        return redirect("/login")

    user = User.query.get_or_404(id)
    return render_template("/users/profile.html", user=user)


# ========= NEED TO USE PATCH METHOD =========
@app.route("/users/<int:id>/update", methods=["GET", "POST"])
def update_user(id):
    """Show user update form and redirect to users page"""

    user = User.query.get(id)

    if id != session[CURR_USER] or "user_id" not in session:
        flash("You do not have permission to do update this user!", "primary")
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


#==============================================================
# VIEW ROUTES
# =============================================================

# ################### HOME PAGE BASIC ###################

# ======= GET RANDOM RECIPES ========
@app.route("/")
def homepage():
    """Show home page with or without auth
    auto populate it with random recipes """
    # SPOONACULAR ENDPOINT
    res = requests.get(f"{BASE_URL}/random", params={ "apiKey": API_KEY, "number": 9 })

    # EDAMAM ENDPOINT
    # res = requests.get(f"{BASE_URL}", params={ "app_id": APP_ID, "app_key": APP_KEY, "to": 9, "q": "grilled steak" })

    data = res.json()

    # EDAMAM
    # recipes = [r['recipe'] for r in data['hits']]

    # return jsonify(recipes)

    # SPOONACULAR
    recipes = data['recipes']

    # Temp data from users.py
    # recipes = [r['recipe'] for r in results['hits']]
    return render_template("index.html", recipes=recipes)


# ======= GET RECIPE BY DIET =========
@app.route("/<diet>")
def show_diets(diet):
    """Show recipes by diets"""
    res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "number": 9 })

    data = res.json()
    recipes = data['results']
    return render_template("index.html", recipes=recipes)


# ########################################################################
# ========= SEARCH FOR A RECIPE WITH CUISINE AND DIETS TEST ROUTES ========




# ########################################################################

# ========= SEARCH FOR A RECIPE WITH CUISINE AND DIETS ========
@app.route("/search")
def search_recipe():
    """Search by diets and cuisines"""
    query = request.args.get('query', "")
    cuisine = request.args.get('cuisine', "")
    diet = request.args.get('diet', "")
    number = 5

    # EDAMAM ENDPOINT
    # if request.args:
    #     response = requests.get(f"{BASE_URL}", params={ "app_id": APP_ID, "app_key": APP_KEY, "to": to, "q": query, "cuisineType": cuisine, "diet": diet })
    #     data = response.json()

        # if len(data['hits']) == 0:
        #     return (jsonify(data=data), 200)


    # SPOONACULAR ENDPOINT
    if request.args:
        res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "cuisine": cuisine, "query": query, "number": number })
        data = res.json()

        if len(data['results']) == 0:
            return (jsonify(data=data), 200)

    recipes = data['results']
    # return jsonify(data=data), 200
    return render_template("index.html", recipes=recipes)


# ########################################################################


# ####################### SHOW RECIPES ######################

@app.route("/recipe/<int:id>")
def show_recipe(id):
    """Show recipe details"""
    # SPOONACULAR ENDPOINT
    # res = requests.get(f"{BASE_URL}/{id}/information?includeNutrition=false", params={ "apiKey": API_KEY })
    res = requests.get(f"https://api.spoonacular.com/recipes/{id}/information?includeNutrition=false", params={ "apiKey": API_KEY })

    # EDAMAM ENDPOINT
    # r_id = requests.utils.quote(uri)
    # res = requests.get(f"{BASE_URL}", params={ "app_id": APP_ID, "app_key": APP_KEY, "r": r_id })
    # res = requests.get("https://api.edamam.com/search?app_id=1bfa73e6&app_key=59669656fdf109339b840b29caad7d34&r=http%3A%2F%2Fwww.edamam.com%2Fontologies%2Fedamam.owl%23recipe_b66666d5c882ca199f43def8f1b8a03f")

    # recipes = [r['recipe'] for r in data['hits']]
    # return url
    # return render_template("index.html", recipes=recipes)

    data = res.json()
    # recipes = [r for r in data]

    # return jsonify(recipes)
    return render_template("views/details.html", recipes=data)

# ########################### TEMP DATA FROM USERS TO FIX HTML ##################################

# @app.route("/users/<string>")
# def details(string):

#     return render_template("/views/details.html", recipes=info)



# ##################### ERROR 404 PAGE ######################

@app.errorhandler(404)
def page_not_found(error):
    """Show 404 ERROR page if page NOT FOUND"""

    return render_template("error.html"), 404

