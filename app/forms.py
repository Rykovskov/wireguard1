from flask_wtf import FlaskForm
from wtforms import Form, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, FieldList, FormField, IntegerField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField()

class AdminUsersForm(FlaskForm):
    id_user = StringField('User ID')
    name_user = StringField('User Name')
    select_user = BooleanField('Selected user', default="unchecked")

class CreateAdminUserForm(FlaskForm):
    new_login = StringField('New login User')
    new_pass  = PasswordField('New Password')
    new_confirm_pass = PasswordField('Confirm New password')
    user_list = FieldList(FormField(AdminUsersForm), min_entries=0)
    new_user = SubmitField("Add user")
    delete_user = SubmitField("Delete user")

