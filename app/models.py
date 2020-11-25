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
        return "<{}:{}>".format(self.ip_allowedips, self.mask_allowedips[:15])


@login_manager.user_loader
def load_user(id_users):
    return db.session.query(Users).get(id_users)


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


class Organizations(db.Model):
    __tablename__ = 'organizations'
    id_organizations = db.Column(db.Integer(), primary_key=True)
    name_organizations = db.Column(db.String(255), nullable=False)
    server_organizations = db.Column(db.String(255))
    public_vpn_key_organizations = db.Column(db.String(255))
    private_vpn_key_organizations = db.Column(db.String(255))
    vpn_users = db.relationship('Vpn_users', backref='vpn_users', lazy='dynamic')


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

    def __repr__(self):
        return "<{}:{}>".format(self.name_vpn_users, self.active_vpn_users)