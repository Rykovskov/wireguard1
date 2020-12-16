# -*- coding: utf-8 -*-
from app import app
from flask import render_template, request, redirect, url_for, flash, make_response, session, send_from_directory
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Vpn_users, Organizations, db, Allowedips, Vpn_key, rebuild_config
from .forms import LoginForm, CreateAdminUserForm, AdminUsersForm, VpnUsersForm, OrganizationsForm, NewVpnUserForm
from werkzeug.datastructures import MultiDict
from sqlalchemy import text
import os
import datetime
from datetime import timedelta

sql_upd_conf = text("update rebuild_config set rebuld=true")


@app.route('/download/wgclient.conf')
def download(filename):
    return send_from_directory('/opt/wireguard1/files', 'wgclient.conf')


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
    view_d = 'on'
    form = VpnUsersForm()
    result = request.form
    res = Vpn_users.query.filter_by(active_vpn_users='True').all()

    if request.method == 'GET':
        print('----------------GET-------------------')
        res = Vpn_users.query.filter_by(active_vpn_users='True').all()
        print('render GET', res)
        form.v_user.data = False
        return render_template('vpn_user.html', form=form, cur_user=current_user.name_users, sp_vpn_users=res)

    if request.method == 'POST':
        print('----------------POST-------------------')
        for k in result.keys():
            print('key - ', k, '---', result[k])

        if 'updt_d' in result.keys():
            form.v_user.data = True
            #print('Показываем отключенных пользователей')
            res = Vpn_users.query.order_by(Vpn_users.name_vpn_users).all()
        if 'updt_e' in result.keys():
            form.v_user.data = False
            #print('Скрываем отключенных пользователей')
            res = Vpn_users.query.filter_by(active_vpn_users='True').all()
        if 'd_user' in result.keys():
            # Делаем пометку что база обнавлена
            r = db.engine.execute(sql_upd_conf)
            #print('#Отключаем выбранных')
            res = Vpn_users.query.order_by(Vpn_users.name_vpn_users).all()
            for u in res:
                if result.get(u.name_vpn_users) == 'on':
                    update_user = Vpn_users.query.filter_by(id_vpn_users=u.id_vpn_users).first()
                    update_user.active_vpn_users = False
                    update_user.dt_disable_vpn_users = datetime.datetime.now()
                    db.session.commit()
            res = Vpn_users.query.filter_by(active_vpn_users='True').all()
        if 'e_user' in result.keys():
            # Делаем пометку что база обнавлена
            r = db.engine.execute(sql_upd_conf)
            res = Vpn_users.query.order_by(Vpn_users.name_vpn_users).all()
            print('#Влючаем выбранных')
            for u in res:
                if result.get(u.name_vpn_users) == 'on':
                    print('6666666666')
                    update_user = Vpn_users.query.filter_by(id_vpn_users=u.id_vpn_users).first()
                    update_user.active_vpn_users = True
                    update_user.dt_disable_vpn_users = datetime.datetime.now()
                    db.session.commit()
            res = Vpn_users.query.filter_by(active_vpn_users='True').all()
        if form.get_setting.data:
            #Cкачиваем настройки
            print(form.get_setting.name)
        if form.new_user.data:
            #print('Показываем форму добавления нового пользователя')
            return redirect(url_for('new_vpn_users'))
        if form.delete_user.data:
            #print('#Показываем форму удаления пользователя')
            for u in res:
                if result.get(u.name_vpn_users) == 'on':
                    del_user = Vpn_users.query.filter_by(id_vpn_users=u.id_vpn_users).first()
                    db.session.delete(del_user)
                    db.session.commit()
            res = Vpn_users.query.filter_by(active_vpn_users='True').all()
        #Проверяем есть запрос на файл настроек
        res1 = Vpn_users.query.order_by(Vpn_users.name_vpn_users).all()
        for un in res1:
            name_key = 'get_'+un[0]
            print(un[0])
            #if name_key in result.keys():
            #    print(name_key)
        print('render POST', res)

        return render_template('vpn_user.html', form=form, cur_user=current_user.name_users, sp_vpn_users=res)



@app.route('/add_vpn_user', methods=['post', 'get'])
@login_required
def new_vpn_users():
    res_org = Organizations.query.order_by(Organizations.name_organizations).all()
    form = NewVpnUserForm()
    form.new_vpn_organizations.choices = res_org
    if request.method == 'POST':
        result = request.form
        if form.save_user.data:
            #Делаем пометку что база обнавлена
            r = db.engine.execute(sql_upd_conf)
            #Сохраняем пользователя
            sql = text("select nextval('vpn_users_id_vpn_users_seq') as ss")
            r = db.engine.execute(sql)
            id_next_vpn_user = int(([row[0] for row in r])[0])+1
            #print(id_next_vpn_user)
            id_org = result['new_vpn_organizations'].split(':')[:-1]
            sp_ip = result['al_ip'].split('\r\n')
            #сохраняем список разрешенных ип
            for ips in sp_ip:
                #Отделяем маску от адреса
                ip_addr, mask = ips.split('/')
                new_allowedips = Allowedips(ip_allowedips=ip_addr, mask_allowedips=mask, vpn_user=id_next_vpn_user)
                db.session.add_all([new_allowedips, ])
                db.session.commit()
            WireGuard = os.path.abspath("/etc/wireguard")
            os.chdir(WireGuard)
            os.system("/usr/bin/wg genkey > privatekey.tmp")
            os.system("/usr/bin/wg pubkey < privatekey.tmp > publickey.tmp")
            f_priv_key = open('privatekey.tmp')
            priv_key = f_priv_key.readline()[:-1:]
            f_priv_key.close()
            f_pub_key = open('publickey.tmp')
            pub_key = f_pub_key.readline()[:-1:]
            f_pub_key.close()
            dt_activ = result.get('date_act')
            dt_disable = result.get('date_dis')
            if dt_disable == '':
                dt_disable = dt_activ + timedelta(days=3366)

             #Вставляем новый VPN key
            new_vpn_key = Vpn_key(publickey=pub_key, privatekey=priv_key)
            db.session.add_all([new_vpn_key, ])
            db.session.commit()
            id_new_vpn = new_vpn_key.id_vpn_key
            act_user = form.now_active.data
            new_vpn_user = Vpn_users(id_vpn_users=id_next_vpn_user,
                                     name_vpn_users=form.new_vpn_login.data,
                                     email_vpn_users=form.email_vpn_users.data,
                                     organizations=id_org[0],
                                     dt_activate_vpn_users=dt_activ,
                                     dt_disable_vpn_users=dt_disable,
                                     vpn_key=id_new_vpn,
                                     active_vpn_users=act_user)
            db.session.add_all([new_vpn_user, ])
            db.session.commit()
            return redirect(url_for('vpn_users'))

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
    return render_template('organizations.html', form=form, cur_user=current_user.name_users, sp_org=res)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))