# Foodie

**Check it out**
[Foodie](https://www.google.com)

## Foodie makes anyone a chef!

When the start button is clicked, random recipes populate the screen, new random recipes can be loaded on the screen by clicking on the Foodie icon or refreshing the page. Users can also get random dietary reciped by clicking on the diet badges right below the navbar. To get more recipes, click the page numbers at the bottom of the page.

Users can also search for a recipe by using the search input in the navbar. Search a recipe by cuisine, diet or ingredient. User do not need to sign up to view recipes.

To save a recipe, a user needs to register/login. Once the user is authenticated, the favorite icon turns red, allowing the user to save any recipe to the database. Users can access their favorited list by clicking on the favorites link on the navbar.

To get details of a recipe, simply click on the recipe card and this will redirect you to a recipe details page, where users can view more information about the recipe, including it's popularity, ingredients and instructions on how to cook the recipe.

From the recipe details page, a user can also print out the recipe details by clicking on the print button.

### Features

- Search annoymously without signing up
- Search by diets, cuisine or ingredient
- Save recipe to favorites
- Print out recipe details, ingredients and instructions

### Demo

![Foodie Demo](/static/images/foodieDemo.gif)

### Data

Foodie uses data from the the Spoonacular API.
Spoonacular API has over 380 thousand recipes to choose from, and an ideal source for a startup app.

### Schema Design

![Schema Design](/static/images/Foodie-schema.png)

### Stacks

**Front End**

- HTML templates using Jinja and WTForms for forms
- Design and interaction using JavaScript, Bootstrap, Font Awesome and raw CSS

**Backend**

- Routes and Models using Python3 and Flask
- SQLAlchemy as a database ORM
- Database using PostgreSQL
- AJAX requests using Axios

**Deployment**

- Deployed on Heroku Server
- Gunicorn server

### Local Environment

To get the code on your local machine, create a PostgreSQL database, and set up a virtual environment in Python, and get an API key from Spoonacular API.

```
> git clone https://github.com/mahdimq/Foodie.git
> python -m venv venv
> pip install -r requirements.txt
> source venv/bin/activate
```

### Improve or Contribute

Feel free to improve or contribute on this. Pull requests are always welcome!

### Author

- [Muhammad Qadir](https://github.com/mahdimq)
