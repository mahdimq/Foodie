import os
from flask import Flask, render_template, redirect, request, g, flash, session, jsonify, make_response
from models import db, connect_db, User, Recipe, Favorite
from secret import key, key2, key3
from forms import SignupForm, LoginForm, EditUserForm
from sqlalchemy.exc import IntegrityError
from helper import diets, cuisines, diet_icons, add_recipe, do_logout
import requests

# ##### TEMP DATA ########
# from users import recipe, diets, results, details, ids

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
OFFSET = 9
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

    g.cuisines = [cuisine for cuisine in cuisines]
    g.diets = [diet for diet in diets]
    g.diet_icons = [icons for icons in diet_icons]

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
    """Handle logout of user."""
    do_logout()
    flash("You have been logged out!", "success")
    return redirect("/")


# #################### DELETE USER ROUTE ####################

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

@app.route("/")
def homepage():
    """show homepage modal explaining website"""

    return render_template("home.html")

# ======= GET RANDOM RECIPES ========
@app.route("/recipes")
def show_recipes():
    """Show home page with or without auth
    auto populate it with random recipes """
    # SPOONACULAR ENDPOINT
    res = requests.get(f"{BASE_URL}/random", params={ "apiKey": API_KEY, "number": 1 })

    data = res.json()
    recipes = data['recipes']
    if len(recipes) == 0:
        flash("Recipe limit reached! Try again later", "warning")
        return render_template("index.html")

    return render_template("index.html", recipes=recipes)


# ======= GET RECIPE BY DIET =========
@app.route("/recipes/<diet>")
def show_diets(diet):
    """Show recipes by diets"""
    res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "number": 1 })

    data = res.json()
    recipes = data['results']

    if len(recipes) == 0:
        flash("Recipe limit reached! Try again later", "warning")
        return render_template("index.html")

    recipe_ids = [r.id for r in g.user.recipes]
    # return jsonify(data)
    return render_template("index.html", recipes=recipes, recipe_ids=recipe_ids)


# ########################################################################

# ========= SEARCH FOR A RECIPE WITH CUISINE AND DIETS ========
@app.route("/search")
def search_recipe():
    """Search by diets and cuisines"""
    query = request.args.get('query', "")
    cuisine = request.args.get('cuisine', "")
    diet = request.args.get('diet', "")
    number = 3

    # SPOONACULAR ENDPOINT
    if request.args:
        res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "cuisine": cuisine, "query": query, "number": number })
        data = res.json()

    if len(data['results']) == 0:
        flash("Sorry, no recipes found!", "danger")
        render_template("index.html")

    recipes = data['results']

    # Make a list of recipes in the DB
    recipe_ids = [r.id for r in g.user.recipes]
    favorites = [f['id'] for f in recipes if f['id'] in recipe_ids]

    return render_template("index.html", recipes=recipes, recipe_ids=recipe_ids, favorites=favorites)

# ####################### SHOW RECIPES DETAILS ######################

@app.route("/recipes/<int:id>")
def show_recipe(id):
    """Show recipe details"""
    # SPOONACULAR ENDPOINT
    res = requests.get(f"{BASE_URL}/{id}/information", params={ "apiKey": API_KEY, "includeNutrition": False })

    data = res.json()

    # return jsonify(data)
    return render_template("views/details.html", recipes=data)

# #################### FAVORITE RECIPE ####################

@app.route("/api/favorite/<int:id>", methods=["POST"])
def favorite_recipe(id):
    """Add to favorites"""

    if not g.user:
        flash("Please login to add recipe to favorites", "danger")
        return redirect("/login")

    # Get recipe from favorites in DB
    recipe = Favorite.query.filter_by(user_id=g.user.id, recipe_id=id).first()
    print("###########################")
    print("RECIPE ADD POST ROUTE: ", recipe)
    print("###########################")
    if not recipe:
        res = requests.get(f"{BASE_URL}/{id}/information", params={ "apiKey": API_KEY, "includeNutrition": False })
        data = res.json()
        recipe = add_recipe(data)

        g.user.recipes.append(recipe)
        db.session.commit()
    else:
        print("###########################")
        print("ERROR in POST ELSE")
        print("###########################")
        g.user.recipes.append(recipe)
        db.session.commit()

    response = jsonify(recipe=recipe.serialize(), message="Recipe has been added!")
    return (response, 200)

# ########################### DELETE FAVORITE HTML ##################################

@ app.route('/api/favorite/<int:id>', methods=['DELETE'])
def remove_favorite(id):
    """ Unfavorite a recipe """
    if not g.user:
        flash("Please login to remove recipe from favorites", "danger")
        return redirect("/login")
    print("###########################")
    print("ID :", id)
    print("###########################")

    try:
        recipe = Recipe.query.filter_by(id=id).first()
        # recipe = Favorite.query.filter_by(user_id=g.user.id, recipe_id=id).first()
        print("###########################")
        print("RECIPE :", recipe)
        print("###########################")
        db.session.delete(recipe)
        db.session.commit()


    except Exception as e:
        print("###########################")
        print("RECIPE ERROR", e)
        print("###########################")
        return jsonify(errors=str(e))

    res = jsonify(recipe=recipe.serialize(), message="Recipe removed!")
    return (res, 200)
    # $$$$$$$$$$$$$$$$$$$$$$$#############################%%%%%%%%%%%%%%%%%%%%%
    # $$$$$$$$$$$$$$$$$$$$$$$#############################%%%%%%%%%%%%%%%%%%%%%
    # $$$$$$$$$$$$$$$$$$$$$$$#############################%%%%%%%%%%%%%%%%%%%%%
    # recipe = Favorite.query.filter_by(user_id=g.user.id, recipe_id=id).first()

    # db.session.delete(recipe)
    # db.session.commit()

    # response_json = jsonify(recipe=recipe.serialize(), message="Recipe removed!")
    # return (response_json, 200)


# ######################## SHOW FAVORITES ###########################

@app.route("/favorites")
def show_favorites():
    """show favorited recipes"""

    if not g.user:
        flash("you must be logged in to view favorites", "danger")
        return redirect("/login")

    # Show ids for recipes in the favorites
    recipe_ids = [r.id for r in g.user.recipes]
    print("##################################################")
    print(recipe_ids)
    print("##################################################")

    return render_template("views/favorites.html", recipe_ids = recipe_ids)

# ###################################################
# ########## TEMP ############

# class PageResult:
#    def __init__(self, data, page = 1, number = 6):
#      self.__dict__ = dict(zip(['data', 'page', 'number'], [data, page, number]))
#      self.full_listing = [self.data[i:i+number] for i in range(0, len(self.data), number)]

#    def __iter__(self):
#      for i in self.full_listing[self.page-1]:
#        yield i

#    def __repr__(self): #used for page linking
#      return "/favorites/{}".format(self.page+1) #view the next page

# @app.route('/favorites/<pagenum>')
# def show_favorites(pagenum):
#     if not g.user:
#         flash("you must be logged in to view favorites", "danger")
#         return redirect("/login")

#     recipe_ids = [r.id for r in g.user.recipes]
#     return render_template('views/favorites.html', listing = PageResult(recipe_ids, pagenum))



# ########## TEMP ############
# ###################################################



# ##################### ERROR 404 PAGE ######################

@app.errorhandler(404)
def page_not_found(error):
    """Show 404 ERROR page if page NOT FOUND"""

    return render_template("error.html"), 404

# ##################### AFTER REQUESTS ######################

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req



# ###################################################
# ###################################################
