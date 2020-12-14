# -*- coding: utf-8 -*-
import os

app_dir = os.path.abspath(os.path.dirname(__file__))
WireGuard_dir = os.path.abspath('/etc/wireguard')


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    SECRET_KEY = 'you-will-never-guess'


class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://flask:freud105b@localhost/WireGuardUsers'


class ProdConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://flask:freud105b@localhost/WireGuardUsers'

