# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import Form, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, FieldList, FormField, IntegerField, PasswordField, SelectField, TextField, DateField, TextAreaField
from wtforms.validators import ValidationError, DataRequired
from wtforms.widgets import TextArea
from .models import Organizations, Vpn_users

def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


def validate_mask(s):
    if len(s) > 2:
        return False
    for x in s:
        if not x.isdigit():
            return False
        i = int(s)
        if i < 16 or i > 32:
            return False
    return True


def adres_check(form, field):
        if not '/' in field.data:
            raise ValidationError('Отсутствует разделить адреса и маски')
        sp_ip = field.data.split('\r\n')
        for ips in sp_ip:
            # Отделяем маску от адреса
            ip_addr, mask = ips.split('/')
            if not (validate_ip(ip_addr) and validate_mask(mask)):
                raise ValidationError('Ошибка в ип адресе')


def adres_vpn_check(form, field):
        sp_ip = Vpn_users.query.filter_by(adres_vpn=field.data).first()
        if not sp_ip is None:
            raise ValidationError('Такой адрес уже есть для другого клиента')


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
    edit_user = SubmitField("Редактировать выбранных")
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
    vpn_login = StringField('ФИО пользователя')
    otdel_user = StringField('Отдел')
    comment_user = StringField('Коментарий')
    active_vpn_users = BooleanField('Статус пользователя ')
    vpn_organizations = StringField('Точка входа')
    allowedips_ip = TextField('IP адрес')
    allowedips_mask = StringField('Маска')
    adres_vpn = StringField('Адрес клиента')
    new_user = SubmitField("Новый пользователь")
    edit_user = SubmitField("Редактировать пользователя")
    delete_user = SubmitField("Удалить выбранных")
    get_setting = SubmitField("Скачать настройки")
    v_user = BooleanField('Visible user ')
    vpn_organizations_sel = SelectField('Точка входа', choices=[(row.id_organizations, row) for row in Organizations.query.all()])
    last_connect_vpn_users = TextField('Последние подключение')

class NewVpnUserForm(FlaskForm):
    new_vpn_login = StringField('ФИО пользователя', validators=[DataRequired()])
    new_vpn_organizations = SelectField('Точка входа')
    email_vpn_users = StringField('E-mail адрес', validators=[DataRequired()])
    otdel_vpn_users = StringField('Отдел')
    comment_vpn_users = StringField('Комментарий')
    allowedips_ip = StringField('IP адрес')
    allowedips_mask = StringField('Маска')
    adres_vpn = StringField('Адрес клиента', validators=[adres_vpn_check])
    adres = TextAreaField('Список доступа:', validators=[adres_check])
    dt_activations = DateField('Дата активации пользователя')
    dt_disable_vpn_users = DateField('Дата отключения пользователя')
    now_active = BooleanField('Активировать', default="checked")
    save_user = SubmitField("Сохранить пользователя")
    cancel_user = SubmitField("Отменить")



class EditVpnUserForm(FlaskForm):
    vpn_login = StringField('ФИО пользователя', validators=[DataRequired()])
    edit_vpn_organizations = SelectField('Точка входа',
                                         render_kw={'disabled': ''},
                                         #validators=[DataRequired()],
                                         choices=[(row.id_organizations, row) for row in Organizations.query.all()])
    #edit_vpn_organizations = StringField(('Точка входа'))
    active_vpn_users = BooleanField('Статус пользователя ')
    email_vpn_users = StringField('E-mail адрес', validators=[DataRequired()])
    otdel_vpn_users = StringField('Отдел')
    comment_vpn_users = StringField('Комментарий')
    allowedips_ip = StringField('IP адреса', widget=TextArea(), validators=[adres_check])
    adres_vpn = StringField('Адрес клиента')
    dt_disable_vpn_users = DateField('Дата отключения пользователя')
    save_user = SubmitField("Сохранить пользователя")
    cancel_user = SubmitField("Отменить")

class OrganizationsForm(FlaskForm):
    id_organizations = IntegerField('Id')
    name_organizations = StringField('Наименование точки входа')
    server_organizations = StringField('IP адрес сервера')
    port = StringField('Порт адрес сервера')
    subnet = StringField('Подсеть')
    public_vpn_key_organizations = StringField('Публичный ключ')
    private_vpn_key_organizations = StringField('Закрытый ключ')
    add_org = SubmitField("Добавить точку входа")
    del_org = SubmitField("Удалить выбранные точки входа")


class Apple_hostsForm(FlaskForm):
    id_apple_hosts = IntegerField('Id')
    host_name = StringField('HostName')
    name_org = SelectField('Точка входа')
    id_org = IntegerField('Id Org')
    add_work_host = SubmitField("Добавить узел")
    del_work_host = SubmitField("Удалить выбранный узел")


class LogginViewForm(FlaskForm):
    id_login = IntegerField('Id')
    user_id = IntegerField('Id')
    admin_name = StringField('Имя администратора')
    descr = StringField('Событие')
    dt_event = DateField('Дата')