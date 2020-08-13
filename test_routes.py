import os
from unittest import TestCase
from models import db, connect_db, User, Recipe, Favorite
from forms import SignupForm, LoginForm, EditUserForm
from app import app, CURR_USER

# create a new TEST DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///foodie_test"
app.config['SQLALCHEMY_ECHO'] = False
app.config['WTF_CSRF_ENABLED'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

# To run test: python -m unittest tes_routes.py

# ########################## USER ROUTES ##########################
#===================================================================

class UsersTestCase(TestCase):
    """Test user routes"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        self.client = app.test_client()

        user = User.register(username="testUser",password="testPassword",email="test@user.com",img_url = "img.url")

        db.session.add(user)
        db.session.commit()

        self.user = user
        self.user_id = user.id
        self.img_url = user.img_url


    def tearDown(self):
        """ Clean up any fouled transactions """
        db.session.rollback()

# ======================== SIGNUP ROUTE ========================

    def test_signup_route(self):
        """Test user registeration"""
        with self.client as client:
            res = client.get('/signup')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('</form>', html)
            self.assertNotIn(b"jibberish", res.data)

# ========================= LOGIN ROUTE =========================

    def test_login_route(self):
        """Test login route with valid user"""
        with self.client as client:
            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Username', html)
            self.assertIn('<h1 class="my-3">Login</h1>', html)
            self.assertNotIn(b"jibberish", res.data)

    def test_login_route_no_user(self):
        """Test login route with no user"""
        with self.client as client:
            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1 class="my-3">Login</h1>', html)
            self.assertNotIn(b"jibberish", res.data)

# ========================= LOGOUT ROUTE =========================

    def test_logout_route(self):
        """Test logout user route"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER] = self.user_id
            res = client.get('/logout', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('You have been succesfully logged out!', html)
            self.assertNotIn(self.img_url, html)
            self.assertNotIn(self.user_id, session)

# ######################### RECIPE ROUTES #########################
#===================================================================

class RecipesTestCase(TestCase):
    """Test recipe routes"""

    def setUp(self):
        """Make demo data."""

        User.query.delete()
        Recipe.query.delete()
        db.session.commit()

        user = User.register(username="testUser",password="testPassword",email="test@user.com",img_url = "img.url")
        recipe = Recipe(title="Fake recipe", image="random.url")

        db.session.add_all([user, recipe])
        db.session.commit()

        self.user = user
        self.user_id = user.id
        self.recipe_id = recipe.id

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

# ======================== RANDOM RECIPES ========================

    def test_random_recipes(self):
        """Test random recipes route"""
        with app.test_client() as client:
            res = client.get("/random")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<div class="diet">', html)
            self.assertIn('<div class="card border mb-4 mx-auto p-1">', html)
            self.assertNotIn(b"jibberish", res.data)

# ========================== DIETS ROUTE ==========================

    def test_diets_route(self):
        """Test recipes from diets route"""
        with app.test_client() as client:
            res = client.get("/recipes/African")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<div class="wrapper">', html)
            self.assertIn('<div class="diets">', html)
            self.assertNotIn(b"jibberish", res.data)

# ======================== FAVORITE RECIPES ========================

    def test_favorites_non_user_route(self):
        """Test unauthorized favorites route"""
        with app.test_client() as client:
            res = client.get("/favorites")
            html = res.get_data(as_text=True)
            """Follow redirect if user not authorized"""
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/login')
            self.assertNotIn(b"jibberish", res.data)

    def test_favorites_route(self):
        """Test authorized favorites route"""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER] = self.user_id
            res = client.get('/favorites', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<title>Favorites</title>', html)
            self.assertNotIn(b"jibberish", res.data)

# ======================== RECIPE DETAILS ========================

    def test_recipe_details_route(self):
        """Test recipe details route"""
        with app.test_client() as client:
            res = client.get("/recipes/1234")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button id="print" class="btn btn-sm"><i class="fas fa-print"></i> - Print Recipe</button>', html)
            self.assertNotIn(b"jibberish", res.data)
