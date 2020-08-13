import os
from flask import Flask, render_template, redirect, request, g, flash, session, jsonify, make_response
from models import db, connect_db, User, Recipe, Favorite
# from config import key #<-- comment out for production
from forms import SignupForm, LoginForm, EditUserForm
from sqlalchemy.exc import IntegrityError
from helper import diets, cuisines, diet_icons, add_recipe, do_logout
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///foodie')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret_recipe')

connect_db(app)

# #################### SPOONACULAR API INFO ########################
BASE_URL = "https://api.spoonacular.com/recipes"
API_KEY = os.environ['KEY']
# API_KEY = key #<-- comment out for production

# ########################## USER SESSION ##########################
CURR_USER = "user_id"

# #################### TO DO BEFORE REQUEST ####################

@app.before_request
def add_user_to_g():
    """If we're logged in, add current user to Flask global."""

    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])

    else:
        g.user = None

    g.cuisines = [cuisine for cuisine in cuisines]
    g.diets = [diet for diet in diets]
    g.diet_icons = [icons for icons in diet_icons]

#==================================================================
#                           USER ROUTES
#==================================================================

# ################### SIGN UP FORM ####################

@ app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle User Registration and Display form"""

    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        image = form.img_url.data or User.img_url.default.arg

        new_user = User.register(username, password, email, image)
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            # Check user input for errors and append to errors
            if "Key (email)" in str(err):
                form.email.errors.append("Email taken, please pick another")
            elif "Key (username)" in str(err):
                form.username.errors.append("Username taken, please pick another")
            return render_template("/users/signup.html", form=form)

        # ADD USER TO SESSION
        session[CURR_USER] = new_user.id
        flash("Thank you for registering", "warning")
        return redirect(f"/users/{new_user.id}")

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
            return redirect("/")
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template("users/login.html", form=form)


# ####################### LOGOUT ROUTE ######################

@app.route('/logout')
def logout():
    """Handle user logout"""
    do_logout()
    flash("You have been succesfully logged out!", "success")
    return redirect("/")


# #################### DELETE USER ROUTE ####################

@app.route("/users/<int:id>/delete", methods=["POST"])
def delete_user(id):
    """Delete user profile"""

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
    """Redirect to user details page"""

    if CURR_USER not in session or id != session[CURR_USER]:
        flash("You must be logged in to view this page", "danger")
        return redirect("/login")

    user = User.query.get_or_404(id)
    return render_template("/users/profile.html", user=user)

# ################### UPDATE USER DETAILS ####################

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
        user.img_url = form.img_url.data or None

        db.session.commit()
        flash('Updated profile successfully', 'info')
        return redirect(f'/users/{id}')
    try:
        return render_template("/users/update.html", form=form, user=user)
    except:
        return ('', 403)

#==================================================================
#                           VIEW ROUTES
#==================================================================

# ########################## HOME PAGE #########################

@app.route("/")
def homepage():
    """show homepage modal explaining website"""

    return render_template("index.html")

# ##################### SHOW RANDOM RECIPES #####################

@app.route("/random")
def show_recipes():
    """Show home page with or without auth
    auto populate it with random recipes """

    # SPOONACULAR ENDPOINT
    res = requests.get(f"{BASE_URL}/random", params={ "apiKey": API_KEY, "number": 8 })

    data = res.json()
    recipes = data['recipes']
    if len(recipes) == 0:
        flash("Recipe limit reached! Try again later", "warning")
        return render_template("index.html")

    return render_template("/views/random.html", recipes=recipes)

# ##################### GET RECIPE BY DIET ######################

@app.route("/recipes/<diet>")
def show_diets(diet):
    """Show recipes by diets"""
    offset = request.args.get('offset')

    # SPOONACULAR ENDPOINT
    res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "number": 8, "offset": offset })

    data = res.json()
    recipes = data['results']

    path = f"/recipes/{diet}?diet={diet}"

    if len(recipes) == 0:
        flash("Recipe limit reached! Try again later", "warning")
        return render_template("index.html")

    # recipe id's already in the user's list
    if g.user:
        recipe_ids = [r.id for r in g.user.recipes]
    else:
        recipe_ids = []

    return render_template("/views/recipes.html", recipes=recipes, recipe_ids=recipe_ids,  offset=offset, url=path)

# ########### SEARCH FOR A RECIPE WITH CUISINE AND DIET ############

@app.route("/search")
def search_recipe():
    """Search by diets and cuisines"""
    query = request.args.get('query', "")
    cuisine = request.args.get('cuisine', "")
    diet = request.args.get('diet', "")
    offset = request.args.get('offset')
    number = 8

    if request.args:
        # SPOONACULAR ENDPOINT
        res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "cuisine": cuisine, "query": query, "number": number, "offset": offset })
        data = res.json()

    if len(data['results']) == 0:
        flash("Sorry, no recipes found!", "danger")
        render_template("/views/random.html")

    recipes = data['results']

    path = f"/search?query={query}&cuisine={cuisine}&diet={diet}"

    # Make a list of recipes in the DB
    if g.user:
        recipe_ids = [r.id for r in g.user.recipes]
    else:
        recipe_ids = []
    # show recipes already in the favorites
    favorites = [f['id'] for f in recipes if f['id'] in recipe_ids]

    return render_template("/views/recipes.html", recipes=recipes, recipe_ids=recipe_ids, favorites=favorites, url=path, offset=offset)

# ################### SHOW RECIPE DETAILS ####################

@app.route("/recipes/<int:id>")
def show_recipe(id):
    """Show recipe details"""
    # SPOONACULAR ENDPOINT
    res = requests.get(f"{BASE_URL}/{id}/information", params={ "apiKey": API_KEY, "includeNutrition": False })

    data = res.json()

    return render_template("views/details.html", recipes=data)

# ######################## SHOW FAVORITES ########################

@app.route("/favorites")
def show_favorites():
    """show favorited recipes"""

    if not g.user:
        flash("you must be logged in to view favorites", "danger")
        return redirect("/login")

    # Show ids for recipes in the favorites
    recipe_ids = [r.id for r in g.user.recipes]

    return render_template("views/favorites.html", recipe_ids=recipe_ids)

# #################### ADD FAVORITE RECIPE ####################

@app.route("/api/favorite/<int:id>", methods=["POST"])
def favorite_recipe(id):
    """Add to favorites"""

    if not g.user:
        flash("Please login to add recipe to favorites", "danger")
        return abort(401)

    # Get recipe from favorites in DB
    recipe = Recipe.query.filter_by(id=id).first()

    if not recipe:
        # SPOONACULAR ENDPOINT
        res = requests.get(f"{BASE_URL}/{id}/information", params={ "apiKey": API_KEY, "includeNutrition": False })
        data = res.json()
        recipe = add_recipe(data)

        g.user.recipes.append(recipe)
        db.session.commit()
    else:
        g.user.recipes.append(recipe)
        db.session.commit()

    response = jsonify(recipe=recipe.serialize(), message="Recipe has been added!")
    return (response, 200)

# ################### REMOVE FAVORITE RECIPE ####################

@ app.route('/api/favorite/<int:id>', methods=['DELETE'])
def remove_favorite(id):
    """ Unfavorite a recipe """
    if not g.user:
        flash("Please login to remove recipe from favorites", "danger")
        return abort(401)

    try:
        recipe = Recipe.query.filter_by(id=id).first()
        db.session.delete(recipe)
        db.session.commit()

    except Exception as e:
        print("RECIPE ERROR", e)
        return jsonify(errors=str(e))

    res = jsonify(recipe=recipe.serialize(), message="Recipe removed!")
    return (res, 200)

# ####################### ERROR 404 PAGE ######################

@app.errorhandler(404)
def page_not_found(error):
    """Show 404 ERROR page if page NOT FOUND"""

    return render_template("error.html"), 404

# ####################### AFTER REQUESTS ######################

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req


