from app import app
from flask import render_template, request, redirect, url_for, flash, make_response, session
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Vpn_users, Organizations, db
from .forms import LoginForm, CreateAdminUserForm, AdminUsersForm, VpnUsersForm, OrganizationsForm, NewVpnUserForm
from werkzeug.datastructures import MultiDict


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


@app.route('/admin', methods=['post', 'get'])
@login_required
def admin():
    res = Users.query.order_by(Users.name_users).all()
    init_merits = [dict(id_user=s.id_users, name_user=s.name_users, select_user='') for s in res]
    useradminform = CreateAdminUserForm(user_list=init_merits)
    if request.method == 'POST':
        result = request.form
        print(result)
        if useradminform.delete_user.data:
            for u in res:
                if result.get(u.name_users) == 'on':
                    del_user = Users.query.filter_by(id_users=u.id_users).first()
                    db.session.delete(del_user)
                    db.session.commit()
        if useradminform.new_user.data:
            if (useradminform.new_login.data != '') and (useradminform.new_pass.data != ''):
                #Проверяем нет ли такого пользователя уже в базе
                q1 = len(Users.query.filter_by(name_users = useradminform.new_login.data).all())
                if q1 == 0:
                    if useradminform.new_pass.data == useradminform.new_confirm_pass.data:
                        print('password confirm')
                        #Создаем пользователя
                        new_user = Users(name_users=useradminform.new_login.data)
                        new_user.set_password(useradminform.new_pass.data)
                        db.session.add_all([new_user,])
                        db.session.commit()
                        print('Crete user complete')
                    else:
                        flash("Пароли не совпадают!!!", 'error')
                        return redirect(url_for('admin'))
                else:
                    flash("Пользователь уже существует!!!", 'error')
                    return redirect(url_for('admin'))
            else:
                flash("Не заполнен логин или пароль!!!", 'error')
                return redirect(url_for('admin'))
        res = Users.query.order_by(Users.name_users).all()
    return render_template('admin.html', form=useradminform, cur_user=current_user.name_users, sp_users=res)


@app.route('/vpn_users', methods=['post', 'get'])
@login_required
def vpn_users():
    res = Vpn_users.query.order_by(Vpn_users.name_vpn_users).all()
    form = VpnUsersForm()
    if request.method == 'POST':
        result = request.form
        print(result)
    return render_template('vpn_user.html', form=form, cur_user=current_user.name_users, sp_users=res)


@app.route('/add_vpn_user', methods=['post', 'get'])
@login_required
def new_vpn_users():
    res = Vpn_users.query.order_by(Vpn_users.name_vpn_users).all()
    form = NewVpnUserForm()
    if request.method == 'POST':
        result = request.form
        print(result)
    return render_template('add_vpn_user.html', form=form, cur_user=current_user.name_users)


@app.route('/org', methods=['post', 'get'])
@login_required
def organizations():
    res = Organizations.query.order_by(Organizations.name_organizations).all()
    form = OrganizationsForm()
    if request.method == 'POST':
        result = request.form
        if form.del_org.data:
            for o in res:
                # Проверяем есть ли пользователи этой организации если есть то удалять нельзя
                try:
                    col_vpn_user = len(Vpn_users.query.filter_by(organizations=o.id_organizations).first())
                except:
                    col_vpn_user = 0
                if col_vpn_user == 0:
                    if result.get(o.name_organizations) == 'on':
                        del_org = Organizations.query.filter_by(id_organizations=o.id_organizations).first()
                        db.session.delete(del_org)
                        db.session.commit()
                else:
                    flash('У организации: '+o.name_organizations+', есть пользователи - удалять нельзя!!!', 'error')
                    return redirect(url_for('organizations'))
        if form.add_org.data:
            #проверяем что все поля заполнены
            if form.name_organizations.data !='' and form.server_organizations.data !='' and form.public_vpn_key_organizations.data != '' and form.private_vpn_key_organizations.data != '':
                #проверяем что такой организации еще нет
                q1 = len(Organizations.query.filter_by(name_organizations=form.name_organizations.data).all())
                if q1 == 0:
                    #Добавляем новую организацию
                    new_org = Organizations(name_organizations=form.name_organizations.data, server_organizations=form.server_organizations.data, public_vpn_key_organizations=form.public_vpn_key_organizations.data, private_vpn_key_organizations=form.private_vpn_key_organizations.data)
                    db.session.add_all([new_org, ])
                    db.session.commit()
                else:
                    flash("Такая организация уже есть!!!", 'error')
                    return redirect(url_for('organizations'))
            else:
                flash("Не все поля заполнены!!!", 'error')
                return redirect(url_for('organizations'))
        res = Organizations.query.order_by(Organizations.name_organizations).all()
    form.private_vpn_key_organizations.data = ''
    form.public_vpn_key_organizations.data = ''
    form.name_organizations.data = ''
    form.server_organizations.data = ''
    return render_template('Organizations.html', form=form, cur_user=current_user.name_users, sp_org=res)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))