from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os, config

app = Flask(__name__)
app.config.from_object(config.DevConfig)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from . import views
