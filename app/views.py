# -*- coding: utf-8 -*-
from app import app
from flask import render_template, request, redirect, url_for, flash, make_response, session, send_from_directory
from flask_login import login_required, login_user, current_user, logout_user
from .models import Users, Vpn_users, Organizations, org_last_addres, db, Allowedips, Vpn_key, rebuild_config, Logging, Logging_view
from .forms import LoginForm, CreateAdminUserForm, AdminUsersForm, VpnUsersForm, OrganizationsForm, NewVpnUserForm, EditAdminUserForm, LogginViewForm
from werkzeug.datastructures import MultiDict
from sqlalchemy import text
import os
import datetime
from datetime import timedelta
import codecs

#Служебные SQL запросы
sql_upd_conf = text("update rebuild_config set rebuld=true")
sql_last_used_ip = text("select id_organizations, name_organizations, server_organizations, port, (select adres_vpn as aa from vpn_users_view where organizations =id_organizations  order by n_ip desc limit 1) from organizations")


@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user.name_users)

@app.route('/Loggin/', methods=['post', 'get'])
@login_required
def Loggin():
    form = LogginViewForm()
    res = Logging_view.query.order_by(Logging_view.name_users).all()
    return render_template('logging.html', form=form, cur_user=current_user.name_users, sp_loggin=res)


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        # Логируем вход пользователя
        new_Logging = Logging(user_id=current_user.id_users, descr='Вход пользователя')
        db.session.add_all([new_Logging, ])
        db.session.commit()
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter(Users.name_users == form.username.data).first()
        if user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            new_Logging1 = Logging(user_id=current_user.id_users, descr='Регистрация пользователя')
            db.session.add_all([new_Logging1, ])
            db.session.commit()
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
        if useradminform.edit_user.data:
            for u in res:
                if result.get(u.name_users) == 'on':
                    return redirect(url_for('edit_admin', id_users=u.id_users))
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
                        #Создаем пользователя
                        new_user = Users(name_users=useradminform.new_login.data)
                        new_user.set_password(useradminform.new_pass.data)
                        db.session.add_all([new_user,])
                        db.session.commit()
                        new_Logging = Logging(user_id=current_user.id_users, descr='Создание пользователя ' + useradminform.new_login.data)
                        db.session.add_all([new_Logging, ])
                        db.session.commit()
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


@app.route('/edit_admin', methods=['post', 'get'])
@login_required
def edit_admin():
    id_user = request.args.get("id_users")
    user = Users.query.get(id_user)
    form = EditAdminUserForm(login=user.name_users, field_user_id=user.id_users)
    if request.method == 'POST':
        if form.save_user.data:
            if form.new_pass.data == form.new_confirm_pass.data:
                # Сохраняем пользователя
                user.set_password(form.new_pass.data)
                user.name_users = form.login.data
                db.session.add(user)
                db.session.commit()
                new_Logging = Logging(user_id=current_user.id_users,
                                      descr='Редактирование пользователя ' + form.login.data)
                db.session.add_all([new_Logging, ])
                db.session.commit()
                return redirect(url_for('admin'))
            else:
                flash("Пароли не совпадают!!!", 'error')
                return redirect(url_for('edit_admin'))
        if form.cancel_user.data:
            return redirect(url_for('admin'))
    return render_template('edit_admin.html', cur_user=current_user.name_users, form=form)


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
                    new_Logging = Logging(user_id=current_user.id_users,
                                          descr='Отключение пользователя ' + u.name_vpn_users)
                    db.session.add_all([new_Logging, ])
                    db.session.commit()
            res = Vpn_users.query.filter_by(active_vpn_users='True').all()
        if 'e_user' in result.keys():
            # Делаем пометку что база обнавлена
            r = db.engine.execute(sql_upd_conf)
            res = Vpn_users.query.order_by(Vpn_users.name_vpn_users).all()
            print('#Влючаем выбранных')
            for u in res:
                if result.get(u.name_vpn_users) == 'on':
                    update_user = Vpn_users.query.filter_by(id_vpn_users=u.id_vpn_users).first()
                    update_user.active_vpn_users = True
                    update_user.dt_disable_vpn_users = datetime.datetime.now()
                    db.session.commit()
                    new_Logging1 = Logging(user_id=current_user.id_users,
                                          descr='Включение пользователя ' + u.name_vpn_users)
                    db.session.add_all([new_Logging1, ])
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
                    new_Logging2 = Logging(user_id=current_user.id_users,
                                          descr='Удаление пользователя ' + u.name_vpn_users)
                    db.session.add_all([new_Logging2, ])
                    db.session.commit()
            res = Vpn_users.query.filter_by(active_vpn_users='True').all()
        #Проверяем есть запрос на файл настроек
        res1 = Vpn_users.query.order_by(Vpn_users.name_vpn_users).all()
        for un in res1:
            name_key = 'get_'+un.name_vpn_users
            if name_key in result.keys():
                print('Генерим файл настроек для пользователя ', un.name_vpn_users)
                new_Logging3 = Logging(user_id=current_user.id_users,
                                       descr='Получение настроек для пользователя ' + un.name_vpn_users)
                db.session.add_all([new_Logging3, ])
                db.session.commit()
                #Получаем пару ключей для пользователя
                res_key = Vpn_key.query.filter_by(id_vpn_key=un.vpn_key).first()
                # Получаем адрес сервера
                res_server = Organizations.query.filter_by(id_organizations=un.organizations).first()
                # Получаем список разрешенных адресов
                res_ip = Allowedips.query.filter_by(vpn_user=un.id_vpn_users).all()
                col_res_ip = Allowedips.query.filter_by(vpn_user=un.id_vpn_users).count()
                conf = []
                conf.append('[Interface]\n')
                conf.append('PrivateKey = ' + res_key.privatekey + '\n')
                conf.append('Address = ' + un.adres_vpn + '\n')
                conf.append('\n')
                conf.append('[Peer]\n')
                conf.append('PublicKey = ' + res_server.public_vpn_key_organizations + '\n')
                #Формируем список разрешенных ип
                al_ip = ''
                if col_res_ip > 1:
                    for ip_adr in res_ip:
                        al_ip = al_ip + str(ip_adr) + ','
                else:
                    al_ip = str(res_ip[0])+','
                al_ip = al_ip[0:-1]
                conf.append('AllowedIPs = ' + al_ip + '\n')
                conf.append('Endpoint =  ' + res_server.server_organizations + ':' + str(res_server.port) + '\n')
                conf.append('PersistentKeepalive = 25\n')
                name_conf = "/opt/wireguard1/files/" + un.name_vpn_users + '.conf'
                #Сохраняем файл
                with codecs.open(name_conf, 'w', encoding='UTF8') as f:
                    for item in conf:
                        f.write("%s" % item)
                f.close()
                f_n = un.name_vpn_users + '.conf'
                return redirect(url_for('download', filename=f_n))

        print('render POST', res)

        return render_template('vpn_user.html', form=form, cur_user=current_user.name_users, sp_vpn_users=res)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('/opt/wireguard1/files/', filename)


@app.route('/add_vpn_user', methods=['post', 'get'])
@login_required
def new_vpn_users():
    #res_org = Organizations.query.order_by(Organizations.name_organizations).all()
    res_org = org_last_addres.query.order_by(org_last_addres.name_organizations).all()
    form = NewVpnUserForm()
    form.new_vpn_organizations.choices = res_org
    #last_adr =
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
            #if dt_disable == '':
            #    dt_disable = dt_activ + timedelta(days=3366)

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
                                     active_vpn_users=act_user,
                                     adres_vpn=form.adres_vpn.data)
            db.session.add_all([new_vpn_user, ])
            db.session.commit()
            new_Logging = Logging(user_id=current_user.id_users,
                                   descr='Создание нового пользователя VPN ' + form.new_vpn_login.data)
            db.session.add_all([new_Logging, ])
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
                        new_Logging = Logging(user_id=current_user.id_users,
                                              descr='Удаление организации ' + o.name_organizations)
                        db.session.add_all([new_Logging, ])
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
                    new_org = Organizations(name_organizations=form.name_organizations.data,
                                            server_organizations=form.server_organizations.data,
                                            port=form.port.date,
                                            subnet=form.subnet.data,
                                            public_vpn_key_organizations=form.public_vpn_key_organizations.data,
                                            private_vpn_key_organizations=form.private_vpn_key_organizations.data)
                    db.session.add_all([new_org, ])
                    db.session.commit()
                    new_Logging1 = Logging(user_id=current_user.id_users,
                                          descr='Добавление организации ' + form.name_organizations.data)
                    db.session.add_all([new_Logging1, ])
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