# -*- coding: utf-8 -*-
import os
from app import app, db
from app.models import Users
from flask_script import Manager, Shell, Server
from flask_migrate import MigrateCommand

manager = Manager(app)

# эти переменные доступны внутри оболочки без явного импорта
def make_shell_context():
    return dict(app=app, db=db, User=Users)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(host='0.0.0.0'))

if __name__ == '__main__':
    manager.run()