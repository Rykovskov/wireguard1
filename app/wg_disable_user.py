#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import datetime

wireguard_patch = '/etc/wireguard'
prefix_wg_config = 'wg_'

conn = psycopg2.connect(dbname='WireGuardUsers', user='flask', password='freud105b', host='localhost')
sql_select_users = """select  id_vpn_users, dt_activate_vpn_users, dt_disable_vpn_users, active_vpn_users from vpn_users"""
sql_update_rebuild = """update rebuild_config set rebuld=true"""
sql_enable_user = """update vpn_users set active_vpn_users=true where id_vpn_users = %s"""
sql_disable_user = """update vpn_users set active_vpn_users=false where id_vpn_users = %s"""
cur = conn.cursor()

# Начинаем обход пользователей
cur.execute(sql_select_users)
user_sp = cur.fetchall()
enable_rebuild = False
for usr in user_sp:
    cur_dt = datetime.datetime.now()
    if (cur_dt > usr[1]) and (usr[3] == False) and (cur_dt < usr[2]):
        print('Активируем пользователя')
        cur.execute(sql_enable_user)
        conn.commit()
        enable_rebuild = True
    if (cur_dt > usr[2]) and (usr[3] == True):
        print('Отключаем пользователя')
        cur.execute(sql_disable_user)
        conn.commit()
        enable_rebuild = True
if enable_rebuild:
    print('Есть изменения, нужно пересобрать конфигурационный файл')
    cur.execute(sql_update_rebuild)
    conn.commit()
