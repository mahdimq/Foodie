import os
from flask import Flask, render_template, redirect, request, g, flash, session, jsonify, make_response
from models import db, connect_db, User, Recipe, Favorite
from secret import key, key2, key3
from forms import SignupForm, LoginForm, EditUserForm
from sqlalchemy.exc import IntegrityError
import requests

# ##### TEMP DATA ########
from users import recipe, diets, results, details, ids

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
API_KEY = key3

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
    # res = requests.get(f"{BASE_URL}/random", params={ "apiKey": API_KEY, "number": 1 })

    # data = res.json()
    print("###########################")
    # print(data)
    print("###########################")
    # recipes = data['recipes']


    # return jsonify(data)
    return render_template("index.html", recipes=recipe)


# ======= GET RECIPE BY DIET =========
@app.route("/recipes/<diet>")
def show_diets(diet):
    """Show recipes by diets"""
    res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "number": 1 })

    data = res.json()
    recipes = data['results']

    recipe_ids = [recipe.id for recipe in g.user.recipes]
    # return jsonify(data)
    return render_template("index.html", recipes=recipes, recipe_ids=recipe_ids)


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
    number = 3

    # SPOONACULAR ENDPOINT
    if request.args:
        res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "cuisine": cuisine, "query": query, "number": number })
        data = res.json()

        if len(data['results']) == 0:
            return (jsonify(data=data), 200)

    recipes = data['results']

    # TEMP CHANGES
    # user_favorites = [fav.id for fav in g.user.recipes]
    # favorites = [r['id'] for r in recipes if r['id'] in user_favorites]
    # return jsonify(data=data, favorites=favorites), 200
    return render_template("index.html", recipes=recipes)
    # return render_template("index.html", recipes=recipes, favorites=favorites)


# ####################### SHOW RECIPES DETAILS ######################

@app.route("/recipes/<int:id>")
def show_recipe(id):
    """Show recipe details"""
    # SPOONACULAR ENDPOINT
    # res = requests.get(f"{BASE_URL}/{id}/information", params={ "apiKey": API_KEY, "includeNutrition": False })

    # data = res.json()
    # recipes = [r for r in data]

    return jsonify(details)
    # return render_template("views/details.html", recipes=data)


# #################### FAVORITE RECIPE ####################
# HELPER FUNCTION
def add_recipe(recipe):
    """Add recipe to favorites tables in the DB"""
    id = recipe.get('id', None)
    title = recipe.get('title', None)
    image = recipe.get('image', None)
    sourceName = recipe.get('sourceName', None)
    sourceUrl = recipe.get('sourceUrl', None)
    readyInMinutes = recipe.get('readyInMinutes', None)
    servings = recipe.get('servings', None)

    favorite_recipe = Recipe(id=id, title=title, image=image, sourceName=sourceName, sourceUrl=sourceUrl, readyInMinutes=readyInMinutes, servings=servings)

    try:
        db.session.add(favorite_recipe)
        db.session.commit()
        print("###########################")
        print("RECIPE FAVORITED")
        print("###########################")
    except Exception:
        db.session.rollback()
        print("###########################")
        print("THIS IS AN EXCEPTION", str(Exception))
        print("###########################")
        # import pdb; pdb.set_trace()
        return "Error in saving recipe. Please try again."
    return favorite_recipe

# #################### FAVORITE RECIPE ####################

@app.route("/api/favorite/<int:id>", methods=["POST"])
def favorite_recipe(id):
    """Add to favorites"""

    if not g.user:
        flash("Please login to add recipe to favorites", "danger")
        return redirect("/login")
        # return abort(401)

    # recipe = Favorite.query.filter_by(user_id=g.user.id, recipe_id=id).first()
    recipe = Favorite.query.filter_by(recipe_id=id).first()

    # #####TEMP##########

    if not recipe:
    # if not favorite_recipe:
        res = requests.get(f"{BASE_URL}/{id}/information", params={ "apiKey": API_KEY, "includeNutrition": False })
        data = res.json()
        print("###########################")
        print("RECIPE :", data)
        print("###########################")
        # import pdb; pdb.set_trace()
        recipe = add_recipe(data)

        CURR_USER.recipes.append(recipe)
        print("###########################")
        print("RECIPE FAVORITED")
        print("###########################")
        db.session.commit()
    else:
        g.user.recipes.append(recipe)
        print("###########################")
        print("RECIPE FAVORITED")
        print("###########################")
        db.session.commit()

    response_json = jsonify(recipe=recipe.serialize(), message="Recipe Added!")
    return (response_json, 200)

# ########################### DELETE FAVORITE HTML ##################################




# ########################### DELETE FAVORITE HTML ##################################

@ app.route('/api/favorite/<int:id>', methods=['DELETE'])
def remove_favorite(id):
    """ Unfavorite a recipe """
    if not g.user:
        flash("Please login to remove recipe from favorites", "danger")
        return redirect("/login")

    try:
        # recipe = Recipe.query.filter_by(id=id).first()
        recipe = Favorite.query.filter_by(user_id=g.user.id, recipe_id=id).first()
        db.session.delete(recipe)
        print("###########################")
        print("RECIPE REMOVED")
        print("###########################")
        db.session.commit()

        response_json = jsonify(recipe=recipe.serialize(), message="Recipe removed!")
        return (response_json, 200)

    except Exception as e:
        print("###########################")
        print("RECIPE ERROR", e)
        print("###########################")
        print(str(e))
        return jsonify(errors=str(e))

# ########################### TEMP DATA FROM USERS TO FIX HTML ##################################
# SHOW FAVORITES ###########################

@app.route("/favorites")
def show_favorites():
    """show favorited recipes"""

    if not g.user:
        flash("you must be logged in to view favorites", "danger")
        return redirect("/login")


    # TEMP #######
    favorites = Favorite.query.filter_by(user_id=g.user.id).all()

    # TEMP #######


    # recipe_ids = [recipe.id for recipe in g.user.recipes]

    return render_template("views/favorites.html", recipe_ids = favorites)


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

################################ TEMP CODE ##################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################

# ==================================================
# # VIEW ROUTES
# # =============================================================

# # ################### HOME PAGE BASIC ###################
# @app.route("/")
# def homepage():
#     """Show home page with or without auth
#     auto populate it with random recipes """
#     if not g.user:
#         return redirect('/login')
#     # get user information from session
#     user = g.user

#     return render_template("home.html", user=user)

# # ################### MAIN RECIPE PAGE ###################

# @app.route("/recipes")
# def view_recipes():
#     """View random recipes"""
#     # SPOONACULAR ENDPOINT
#     # res = requests.get(f"{BASE_URL}/random", params={ "apiKey": API_KEY, "number": 1 })

#     result = recipe
#     # result = [r for r in recipe['results']]

#     # data = res.json()
#     # recipes = data['recipes']

#     # session['recipes'] = recipes
#     return render_template("index.html", recipes=result)

# # ################### SEARCH RECIPE PAGE ###################

# @app.route("/search")
# def search_recipe():
#     """Search by diets and cuisines"""
#     if not g.user:
#         return abort(401)

#     query = request.args.get('query', "")
#     cuisine = request.args.get('cuisine', "")
#     diet = request.args.get('diet', "")
#     offset = int(request.args.get('offset', 0))
#     number = 3

#     # SPOONACULAR ENDPOINT
#     if request.args:
#         res = requests.get(f"{BASE_URL}/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "cuisine": cuisine, "query": query, "number": number })
#         data = res.json()

#         if len(data['results']) == 0:
#             return (jsonify(data=data), 200)

#     user_favorites = [f.id for f in g.user.recipes]
#     favorites = [r['id'] for r in data['results'] if r['id'] in user_favorites]
#     response_json = jsonify(data=data, favorites=favorites)

#     return (response_json, 200)

#############################################################################
#############################################################################
#############################################################################
#############################################################################
