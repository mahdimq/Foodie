import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """ Connect to Database """
    db.app = app
    db.init_app(app)


# class User(db.Model):
#     """ User Model """
#     __tablename__ = 'users'

#     id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
#     username = db.Column(db.String(20), unique=True)
#     password = db.Column(db.Text, nullable=False)
#     email = db.Column(db.String(50), nullable=False, unique=True)
#     img_url = db.Column(db.String, default='/static/images/chef.jpg')

#     recipes = db.relationship('Recipe', secondary="favorites", backref='users')

#     @classmethod
#     def register(cls, username, password, email, img_url):
#         """Register user with hashed password & return user."""

#         hashed = bcrypt.generate_password_hash(password)
#         # turn bytestring into normal (unicode ut(8) string)
#         hashed_utf8 = hashed.decode("utf8")
#         # create user
#         user = cls(
#             username=username,
#             password=hashed_utf8,
#             img_url=img_url,
#             email=email
#         )

#         # return instance of user with username and hashed password
#         return user

#     @classmethod
#     def authenticate(cls, username, password):
#         """ Validate user exists & pwd is correct
#         return user if valid; else return False
#         """

#         u = User.query.filter_by(username=username).first()
#         if u and bcrypt.check_password_hash(u.password, password):
#             # return user instance
#             return u
#         else:
#             return False


#     @classmethod
#     def serialize(self):
#         """ Serialize User instance for JSON """
#         return {
#             'id': self.id,
#             'username': self.username,
#             'email': self.email,
#             'img_url': self.img_url,
#         }

#     def __repr__(self):
#         return f'<User= username:{self.username} email:{self.email} >'


# class Favorite(db.Model):
#     """ Many to Many Users to Recipes """
#     __tablename__ = "favorites"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), primary_key=True)
#     recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
#     date = db.Column(db.DateTime, default=datetime.datetime.now())

#     def friendly_date(self):
#         """Create friendly date"""
#         date = self.created_at.strftime("%a %b %d %Y,  %-I:%M %p")
#         return date

# class Recipe(db.Model):
#     """ Recipe Model """
#     __tablename__ = 'recipes'

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String, nullable=False)
#     image = db.Column(db.String, nullable=False)
#     sourceName = db.Column(db.String)
#     sourceUrl = db.Column(db.String)
#     readyInMinutes = db.Column(db.Integer)
#     servings = db.Column(db.Integer)

#     def __repr__(self):
#         return f'<Recipe=  title:{self.title}, source_name:{self.sourceName}>'

#     def serialize(self):
#         """ Serialize Recipe instance for JSON """
#         return {
#             'id': self.id,
#             'title': self.title,
#             'img_url': self.image,
#             'source_name': self.sourceName,
#             'source_url': self.sourceUrl,
#             'prep_time': self.readyInMinutes,
#             'serves': self.servings
#         }

# recipe image default="https://tinyurl.com/y5phz2pk"

# ######################### NEW MODELS TEST ###########################

class User(db.Model):
    """Create a schema table for users"""
    __tablename__ = 'users'

    def __repr__(self):
        u = self
        return f"<User id={u.id} firstname={u.firstname} lastname={u.lastname} image_url={u.image_url}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    img_url = db.Column(db.String, default='/static/images/chef.jpg')

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

    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='cascade'), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now())

    def friendly_date(self):
        """Create friendly date"""
        date = self.created_at.strftime("%a %b %d %Y,  %-I:%M %p")
        return date


class Recipe(db.Model):
    """ Recipe Model """
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    sourceName = db.Column(db.String)
    sourceUrl = db.Column(db.String)
    readyInMinutes = db.Column(db.Integer)
    servings = db.Column(db.Integer)

    users = db.relationship('User', secondary="favorites", backref="recipes", lazy=True)

    def __repr__(self):
        return f'<Recipe=  title:{self.title}, source_name:{self.sourceName}>'

    def serialize(self):
        """ Serialize Recipe instance for JSON """
        return {
            'id': self.id,
            'title': self.title,
            'img_url': self.image,
            'source_name': self.sourceName,
            'source_url': self.sourceUrl,
            'prep_time': self.readyInMinutes,
            'serves': self.servings
        }

# #####################################################################
