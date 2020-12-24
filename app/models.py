# -*- coding: utf-8 -*-
from app import db, login_manager
from datetime import datetime
from flask_login import (LoginManager, UserMixin, login_required,
			  login_user, current_user, logout_user)
from werkzeug.security import generate_password_hash, check_password_hash


class Allowedips(db.Model):
    __tablename__ = 'allowedips'
    id_allowedips = db.Column(db.Integer(), primary_key=True)
    ip_allowedips = db.Column(db.String(15), nullable=False)
    mask_allowedips = db.Column(db.String(15), nullable=False)
    vpn_user = db.Column(db.Integer, db.ForeignKey('vpn_users.id_vpn_users'))

    def __repr__(self):
        return "{}/{}".format(self.ip_allowedips, self.mask_allowedips[:15])


@login_manager.user_loader
def load_user(id_users):
    return db.session.query(Users).get(id_users)


class rebuild_config:
    __tablename__ = 'rebuild_config'
    rebuld = db.Column(db.Boolean())
    last_update = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.rebuld, self.last_update)

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id_users = db.Column(db.Integer(), primary_key=True)
    name_users = db.Column(db.String(255), nullable=False)
    pas_users = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<{}:{}>".format(self.id_users, self.name_users)

    def set_password(self, password):
            self.pas_users = generate_password_hash(password)

    def check_password(self, password):
            return check_password_hash(self.pas_users, password)

    def get_id(self):
            return self.id_users


class Vpn_key(db.Model):
    __tablename__ = 'vpn_key'
    id_vpn_key = db.Column(db.Integer(), primary_key=True)
    publickey = db.Column(db.String(15), nullable=False)
    privatekey = db.Column(db.String(15), nullable=False)
    def __repr__(self):
        return "<{}:{}>".format(self.publickey, self.privatekey)


class org_last_addres(db.Model):
    __tablename__ = 'org_last_addres'
    id_organizations = db.Column(db.Integer(), primary_key=True)
    name_organizations = db.Column(db.String(255))
    server_organizations = db.Column(db.String(255))
    port = db.Column(db.Integer())
    subnet = db.Column(db.String(255))
    last_ip = db.Column(db.String(255))
    def __repr__(self):
        return "{}:  {} Srv: {}:{} LastIP: {}".format(self.id_organizations, self.name_organizations, self.server_organizations, self.port, self.last_ip)


class Organizations(db.Model):
    __tablename__ = 'organizations'
    id_organizations = db.Column(db.Integer(), primary_key=True)
    name_organizations = db.Column(db.String(255), nullable=False)
    server_organizations = db.Column(db.String(255))
    public_vpn_key_organizations = db.Column(db.String(255))
    private_vpn_key_organizations = db.Column(db.String(255))
    vpn_users = db.relationship('Vpn_users', backref='vpn_users', lazy='dynamic')
    port = db.Column(db.Integer(), nullable=False)
    subnet = db.Column(db.String(255))
    def __repr__(self):
        return "{}:  {} Srv: {}:{} ".format(self.id_organizations, self.name_organizations, self.server_organizations, self.port)


class Vpn_users(db.Model):
    __tablename__ = 'vpn_users'
    id_vpn_users = db.Column(db.Integer(), primary_key=True)
    name_vpn_users = db.Column(db.String(255), nullable=False)
    email_vpn_users = db.Column(db.String(255), nullable=False)
    vpn_key = db.Column(db.Integer(), nullable=False)
    dt_create_vpn_users = db.Column(db.DateTime(), default=datetime.utcnow)
    dt_activate_vpn_users = db.Column(db.DateTime(), default=datetime.utcnow)
    dt_disable_vpn_users = db.Column(db.DateTime())
    active_vpn_users = db.Column(db.Boolean())
    organizations = db.Column(db.Integer, db.ForeignKey('organizations.id_organizations'))
    allowedips = db.relationship('Allowedips', backref='allowedips', lazy='dynamic')
    name_org =  db.relationship('Organizations', backref='organizations',  lazy="select", uselist=False)
    adres_vpn = db.Column(db.String(15), nullable=False)

    @property
    def dt_create_vpn_usersstr(self):
        return self.dt_create_vpn_users.strftime("%d.%m.%Y %H:%M")

    @property
    def dt_activate_vpn_usersstr(self):
        return self.dt_activate_vpn_users.strftime("%d.%m.%Y %H:%M")

    @property
    def dt_disable_vpn_usersstr(self):
        return self.dt_disable_vpn_users.strftime("%d.%m.%Y %H:%M")

    def __repr__(self):
        return "<{}:  {}>".format(self.name_vpn_users, self.active_vpn_users)


class Logging(db.Model):
    __tablename__ = 'logging'
    id_login = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), nullable=False)
    dt_event = db.Column(db.DateTime(), default=datetime.utcnow)
    descr = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<{}:  {}>".format(self.user_id, self.descr)


class Logging_view(db.Model):
    __tablename__ = 'logging_view'
    id_login = db.Column(db.Integer(), primary_key=True)
    name_users = db.Column(db.String(255))
    descr = db.Column(db.String(255))
    dt_event = db.Column(db.DateTime())

    def __repr__(self):
        return "<Админ: {}: Событие: {} Время: {}>".format(self.name_users, self.descr, self.dt_event)

class Iptable_rules(db.Model):
    __tablename__ = 'iptables_rules'
    id  = db.Column(db.Integer(), primary_key=True)
    vpn_user = db.Column(db.Integer, nullable=False)
    rules = db.Column(db.Text(), nullable=False)
    active_rules = db.Column(db.Boolean(), default=False)