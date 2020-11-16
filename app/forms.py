from flask_wtf import FlaskForm
from wtforms import Form, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField()

class CreateAdminUserForm(FlaskForm):
    login = StringField('login', validators = [DataRequired()])
    Password = StringField('Password', validators=[DataRequired()])
    Confirm_Password = StringField('Confirm_Password', validators=[DataRequired()])
    submit = SubmitField()