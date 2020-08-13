import os
from unittest import TestCase
from models import db, User, Recipe
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
from app import app

# create a new TEST DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///foodie_test"
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

# To run test: python -m unittest test_models.py

class ModelsTestcase(TestCase):
    """Unit tests for models schema"""

    def setUp(self):
        """Create test user, add sample data."""

        User.query.delete()
        Recipe.query.delete()

        self.client = app.test_client()

        user = User(username="testUser",password="testPassword",email="test@user.com",img_url = "img.url")
        recipe = Recipe(title="Fake recipe",image="random.url")

        db.session.add_all([user, recipe])
        db.session.commit()

        self.user = user
        self.user_id = user.id
        self.username = user.username
        self.email = user.email
        self.recipe = recipe
        self.recipe_id = recipe.id

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

# ############################ USER MODEL ############################
#======================================================================

    def test_user_model(self):
        """Test base model schema"""

        user = self.user
        """User tables should be empty"""
        self.assertEqual(user.img_url, 'img.url')
        self.assertEqual(len(user.recipes), 0)

    def test_user_repr(self):
        """Test the representation method"""
        user = self.user

        self.assertEqual(
            str(user), f'<User= id:{self.user_id} username:{self.username} email:{self.email}>')

# ======================== USER REGISTRATION ========================

    def test_user_registration(self):
        """Test user registration method """

        new_user = User.register('testUser2', 'testPassword', 'test2@user.com', 'img.url')
        db.session.add(new_user)
        db.session.commit()
        user_test = User.query.filter_by(username='testUser2').first()
        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username, 'testUser2')
        self.assertNotEqual(user_test.password, 'testPassword')
        self.assertEqual(user_test.email, 'test2@user.com')
        self.assertEqual(user_test.img_url, 'img.url')

    def test_invalid_user_registration(self):
        """Test user validation errors"""
        new_user = User.register('testUser3', 'testPassword', 'test3@user.com', 'img.url')
        db.session.add(new_user)
        db.session.commit()
        # A new user cannot have the same username or email
        invalid_user = User.register('testUser3', 'testPassword', 'test3@user.com', 'img.url')

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.add(invalid_user)
            db.session.commit()

# ======================== FAVORITES MODEL ========================

    def test_favorites_model(self):
        """Test favorites model"""
        user = self.user
        recipe = self.recipe

        # Recipe not in user favorites
        self.assertNotIn(recipe, user.recipes)
        # User has one favorite recipe
        user.recipes.append(recipe)
        db.session.commit()
        # Check if instance methods reflect change
        self.assertIn(recipe, user.recipes)

# ########################### RECIPE MODEL ###########################
#======================================================================

    def test_recipe_model(self):
        """Test base model schema"""
        recipe = self.recipe
        self.assertEqual(recipe.id, self.recipe_id)
        self.assertIsInstance(recipe, Recipe)
        self.assertEqual(recipe.title, "Fake recipe")
        self.assertEqual(recipe.image, "random.url")

# ========================== ADD NEW RECIPE ==========================

    def test_new_recipe(self):
        """Test Adding new a recipe to user favorites"""
        user = self.user
        new_recipe = Recipe(title='Fake recipe 2', image="random2.url")
        self.user.recipes.append(new_recipe)
        db.session.commit()

        self.assertEqual(user.recipes[0].title, new_recipe.title)
        self.assertEqual(user.recipes[0].image, new_recipe.image)
        self.assertIn(new_recipe, user.recipes)
        self.assertEqual(len(user.recipes), 1)