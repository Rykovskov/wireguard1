# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import Form, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, FieldList, FormField, IntegerField, PasswordField, SelectField, TextField, DateField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
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
    edit_user = SubmitField("Редактировать")
    new_user = SubmitField("Добавить")
    delete_user = SubmitField("Удалить выбранных")


class EditAdminUserForm(FlaskForm):
    login = StringField('Login')
    new_pass = PasswordField('Пароль:')
    new_confirm_pass = PasswordField('Подтверждение пароля')
    field_user_id = IntegerField('user_id')
    save_user = SubmitField("Сохранить")
    cancel_user = SubmitField("Отменить")


class VpnUsersForm(FlaskForm):
    vpn_login = StringField('Имя пользователя')
    vpn_organizations = StringField('Организация')
    allowedips_ip = TextField('IP адрес')
    allowedips_mask = StringField('Маска')
    adres_vpn = StringField('Адрес клиента')
    new_user = SubmitField("Новый пользователь")
    edit_user = SubmitField("Редактировать пользователя")
    delete_user = SubmitField("Удалить выбранных")
    get_setting = SubmitField("Скачать настройки")
    v_user = BooleanField('Visible user ')

class NewVpnUserForm(FlaskForm):
    new_vpn_login = StringField('Имя пользователя')
    new_vpn_organizations = SelectField('Организация')
    email_vpn_users = StringField('E-mail адрес')
    allowedips_ip = StringField('IP адрес')
    allowedips_mask = StringField('Маска')
    adres_vpn = StringField('Адрес клиента')
    dt_activations = DateField('Дата активации пользователя')
    dt_disable_vpn_users = DateField('Дата отключения пользователя')
    now_active = BooleanField('Активировать', default="checked")
    save_user = SubmitField("Сохранить пользователя")
    cancel_user = SubmitField("Отменить")


class OrganizationsForm(FlaskForm):
    id_organizations = IntegerField('Id')
    name_organizations = StringField('Наименование организации')
    server_organizations = StringField('IP адрес сервера')
    public_vpn_key_organizations = StringField('Публичный ключ')
    private_vpn_key_organizations = StringField('Закрытый ключ')
    add_org = SubmitField("Добавить организацию")
    del_org = SubmitField("Удалить выбранные организации")