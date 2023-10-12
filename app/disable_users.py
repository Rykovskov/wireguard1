#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import os
import datetime

main_host = '10.200.98.3'
conn_m = psycopg2.connect(dbname='WireGuardUsers', user='flask', password='freud105b', host=main_host)
cur_m = conn_m.cursor()

sql_select_org = """select organizations from public.vpn_users
                             where dt_disable_vpn_users<now() and active_vpn_users"""


sql_disable = """update public.vpn_users set active_vpn_users=false
                 where dt_disable_vpn_users<now() and active_vpn_users"""

sql_upd_conf = "insert into rebuild_config (rebuld, org) values (true, %s)"

cur_m.execute(sql_select_org)
org_sp = cur_m.fetchall()
#Отключаем пользователей у которых истек срок
cur_m.execute(sql_disable)
conn_m.commit()
#Проходимся по списку организаций где нужно пересобрать конфиги wireguard
for org in org_sp:
    #print(org[0])
    #Обновляем ребилд конфиг для организации где нужно отключиить пользователей
    cur_m.execute(sql_upd_conf, (org,))
    conn_m.commit()