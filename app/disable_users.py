#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import os
import datetime

#main_host = '10.200.98.3'
main_host = 'localhost'
conn_m = psycopg2.connect(dbname='WireGuardUsers', user='flask', password='freud105b', host=main_host)
cur_m = conn_m.cursor()

sql_select_org = """select organizations from public.vpn_users
                             where dt_disable_vpn_users<now() and active_vpn_users"""

sql_sp_users_disable = "select name_vpn_users from vpn_users where dt_disable_vpn_users<now() and active_vpn_users"

sql_disable = """update public.vpn_users set active_vpn_users=false
                 where dt_disable_vpn_users<now() and active_vpn_users"""

sql_upd_conf = "insert into rebuild_config (rebuld, org) values (true, %s)"

sql_logged = """insert into logging (user_id,descr) values (0,%s)"""

cur_m.execute(sql_select_org)
org_sp = cur_m.fetchall()
#Формируем список отключаемых пользователей
cur_m.execute(sql_sp_users_disable)
sp_disable_users = cur_m.fetchall()
if len(sp_disable_users) > 0:
    for us in sp_disable_users:
        try:
            str1 = "Автомотическое отключение пользователя {}".format(us)
            #print(str1)
            cur_m.execute(sql_logged, (str1,))
            conn_m.commit()
        except:
            print('Недоступен главный сервер БД')
#Отключаем пользователей у которых истек срок
cur_m.execute(sql_disable)
conn_m.commit()
#Проходимся по списку организаций где нужно пересобрать конфиги wireguard
for org in org_sp:
    #Обновляем ребилд конфиг для организации где нужно отключиить пользователей
    try:
        cur_m.execute(sql_upd_conf, (org,))
    except:
        print('Недоступен главный сервер БД')
    conn_m.commit()