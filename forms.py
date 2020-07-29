""" Form Models """

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import URLField, EmailField
from wtforms.validators import InputRequired, Email, Length, Optional


class SignupForm(FlaskForm):
    """ User signup form  """
    username = StringField("Username", validators=[InputRequired(message="Username required")])
    password = PasswordField("Password", validators=[InputRequired(message="Password required")])
    email = EmailField("Email", validators=[InputRequired(message="Email required"), Email(message="Invalid email")])
    img_url = URLField('Profile Image (optional)', validators=[Optional()])

class LoginForm(FlaskForm):
    """ User login form """
    username = StringField("Username", validators=[InputRequired(message="Username required")])
    password = PasswordField("Password", validators=[InputRequired(message="Password required")])

class EditUserForm(FlaskForm):
    """Form for editing users."""
    username = StringField("Username", validators=[InputRequired()])
    # password = PasswordField("Password", validators=[InputRequired(message="Password required")])
    email = StringField("E-mail", validators=[InputRequired(), Email()])
    img_url = URLField('Profile Image (optional)', validators=[Optional()])
