from flask_wtf import FlaskForm
from wtforms import Form, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, FieldList, FormField, IntegerField, PasswordField, SelectField, TextField
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
    new_login = StringField('Login')
    new_pass  = PasswordField('Пароль:')
    new_confirm_pass = PasswordField('Подтверждение пароля')
    user_list = FieldList(FormField(AdminUsersForm), min_entries=0)
    new_user = SubmitField("Добавить")
    delete_user = SubmitField("Удалить выбранных")


class VpnUsersForm(FlaskForm):
    vpn_login = StringField('Имя пользователя')
    vpn_organizations = StringField('Организация')
    allowedips_ip = TextField('IP адрес')
    allowedips_mask = StringField('Маска')
    new_user = SubmitField("Новый пользователь")
    edit_user = SubmitField("Редактировать пользователя")
    delete_user = SubmitField("Удалить выбранных")


class NewVpnUserForm(FlaskForm):
    new_vpn_login = StringField('Имя пользователя')
    new_vpn_organizations = SelectField('Организация')
    allowedips_ip = StringField('IP адрес')
    allowedips_mask = StringField('Маска')
    save_user = SubmitField("Редактировать пользователя")
    cancel_user = SubmitField("Удалить выбранных")