from models import db, connect_db, User, Recipe, Favorite
from flask import request, session
import os

CURR_USER = "user_id"

cuisines = ['african', 'chinese', 'japanese', 'korean', 'vietnamese', 'thai', 'indian', 'british', 'irish', 'french', 'italian', 'mexican','spanish', 'middle eastern', 'jewish', 'american', 'cajun', 'southern', 'greek', 'german', 'nordic', 'eastern european', 'caribbean', 'latin american']
diets = ['pescetarian', 'lacto vegetarian', 'ovo vegetarian', 'vegan', 'vegetarian']
diet_icons = [{'name': 'Pescetarian','image': "https://tinyurl.com/y5c4yu2q"},{'name': 'Lacto-Vegatarian','image': "https://tinyurl.com/y3wuwzr2"},{'name': 'Ovo-Vegetarian','image': "https://tinyurl.com/yxtut8pn"},{'name': 'Vegan','image': "https://tinyurl.com/y2x72gto"},{'name': 'Vegetarian','image': "https://tinyurl.com/y55rcmnz"}]



# Helper function to add recipe to DB
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

    except Exception:
        db.session.rollback()
        print("THIS IS AN EXCEPTION", str(Exception))
        return "ERROR OCCURED IN SAVING RECIPE, PLEASE TRY AGAIN", str(Exception)
    return favorite_recipe


def do_logout():
    """Logout user."""
    if CURR_USER in session:
      session.pop(CURR_USER)

def num_of_pages(self, total_recipes):
        return math.floor(total_recipes / OFFSET)

def paginatination(page):
  """Renders pages"""


def get_recipes(self, page):
      offset = int(page) * OFFSET
      url = f"https://api.spoonacular.com/recipes/complexSearch?cuisine=vietnamese&number={PER_PAGE}&apiKey={API_KEY}&offset={offset}"
      response = requests.get(url)
      return response