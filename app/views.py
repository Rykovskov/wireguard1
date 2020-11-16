from app import app
from flask import render_template, request, redirect, url_for, flash, make_response, session
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, db
from .forms import LoginForm, CreateAdminUserForm


@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user.name_users)


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter(Users.name_users == form.username.data).first()
        if user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('admin'))
        flash("Invalid username/password", 'error')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/admin/', methods=['post', 'get'])
@login_required
def admin():
    form = CreateAdminUserForm()
    res = Users.query.order_by(Users.name_users).all()

    if form.validate_on_submit():
        print(form.login.data)
        if form.login.data != '':
            print('1111111111111')
            #Проверяем нет ли такого пользователя уже в базе
            q1 = len(Users.query.filter_by(name_users = form.login.data).all())
            print('Col user - ', q1)
            if q1 == 0:
                print(form.Password.data)
                print(form.Confirm_Password.data)
                if form.Password.data == form.Confirm_Password.data:
                    print('password confirm')
                    #Создаем пользователя
                    new_user = Users(name_users=form.login.data)
                    new_user.set_password(form.Password.data)
                    db.session.add_all([new_user,])
                    db.session.commit()
                    print('Crete user complete')
                    res = Users.query.order_by(Users.name_users).all()
                    return render_template('admin.html', form=form, cur_user=current_user.name_users, sp_users=res)
    return render_template('admin.html', form=form, cur_user=current_user.name_users, sp_users=res)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))
