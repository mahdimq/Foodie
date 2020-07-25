import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """ Connect to Database """
    db.app = app
    db.init_app(app)


class User(db.Model):
    """ User Model """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    img_url = db.Column(db.String, default='/static/images/chef.jpg')

    recipes = db.relationship('Recipe', secondary="favorites", backref='users')

    @classmethod
    def register(cls, username, password, email, img_url):
        """Register user with hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode ut(8) string)
        hashed_utf8 = hashed.decode("utf8")
        # create user
        user = cls(
            username=username,
            password=hashed_utf8,
            img_url=img_url,
            email=email
        )

        # return instance of user with username and hashed password
        return user

    @classmethod
    def authenticate(cls, username, password):
        """ Validate user exists & pwd is correct
        return user if valid; else return False
        """

        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, password):
            # return user instance
            return u
        else:
            return False


    @classmethod
    def serialize(self):
        """ Serialize User instance for JSON """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'img_url': self.img_url,
        }

    def __repr__(self):
        return f'<User= username:{self.username} email:{self.email} >'


class Favorite(db.Model):
    """ Many to Many Users to Recipes """
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now())

    def friendly_date(self):
        """Create friendly date"""
        date = self.created_at.strftime("%a %b %d %Y,  %-I:%M %p")
        return date

class Recipe(db.Model):
    """ Recipe Model """
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    sourceName = db.Column(db.String)
    sourceUrl = db.Column(db.String)

    def __repr__(self):
        return f'<Recipe=  title:{self.title}, source_name:{self.sourceName}>'

    def serialize(self):
        """ Serialize Recipe instance for JSON """
        return {
            'id': self.id,
            'title': self.title,
            'img_url': self.image,
            'source_name': self.sourceName,
            'source_url': self.sourceUrl
        }


# class Ingredient(db.Model):
#     """ Ingredient Model """

#     __tablename__ = 'ingredients'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False, unique=True)

#     def __repr__(self):
#         return f'<Ingredient: {self.name}>'

#     def serialize(self):
#         """ Serialize Ingredient instance for JSON """
#         return {
#             'id': self.id,
#             'name': self.name,
#         }


# class Step(db.Model):
#     """ Step Model """

#     __tablename__ = 'steps'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
#     number = db.Column(db.Integer)
#     step = db.Column(db.String)

#     def __repr__(self):
#         return f'<Step: {self.number} - {self.step}>'

#     def show_step(self):
#         """ returns a string of the step number and instructions """
#         return f"{self.number}. {self.step}"

#     def serialize(self):
#         """ Serialize Ingredient instance for JSON """
#         return {
#             'id': self.id,
#             'recipe_id': self.recipe_id,
#             'number': self.number,
#             'step': self.step
#         }