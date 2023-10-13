#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import os
import datetime
import transliterate
import codecs
import socket

hostname = socket.gethostname()
wireguard_patch = '/etc/wireguard'
prefix_wg_config = 'wg_'
ip_tables_name_file = '/etc/wireguard/iptables.sh'
#main_host = '10.200.98.3'
main_host = 'localhost'
conn = psycopg2.connect(dbname='WireGuardUsers', user='flask', password='freud105b', host=main_host)
cur = conn.cursor()

sql_select_org = """select id_organizations, name_organizations, server_organizations, public_vpn_key_organizations, 
                    private_vpn_key_organizations, port, subnet, 
                    replace(subnet,'.1/', '.0/') as subnet_1 from organizations 
                    where    (id_organizations = %s) and (select rebuld from public.rebuild_config where org =%s order by last_update desc limit 1)"""

sql_select_all_org = """select id_organizations, name_organizations, server_organizations, public_vpn_key_organizations, 
                    private_vpn_key_organizations, port, subnet, 
                    replace(subnet,'.1/', '.0/') as subnet_1 from organizations 
                    where  id_organizations = %s"""

sql_select_users = """select  id_vpn_users, adres_vpn, 
                      (select publickey from vpn_key where id_vpn_key=vpn_users.vpn_key) as p_key, 
                       replace(cyrillic_transliterate(name_vpn_users),' ','_') as n_user
                       from vpn_users where active_vpn_users=true and organizations =  %s"""
sql_select_allowips = """select ip_allowedips||'/'||mask_allowedips from public.allowedips where vpn_user= %s"""
sql_update_rebuild = """update rebuild_config set rebuld=false where org = %s"""
sql_logged = """insert into logging (user_id,descr) values (0,%s)"""
sql_filter_rules = """select * from iptables_rules where vpn_user = %s and active_rules=true"""
sl_select_work_hosts = "select id_organizations, host_name from hosts_sp"

WireGuard = os.path.abspath(wireguard_patch)
os.chdir(WireGuard)
# выбираем какие организации должны быть на данном хосте
cur.execute(sl_select_work_hosts)
host_sp = cur.fetchall()
#Заполняем файл iptables
ipt = []
ipt.append('#!/bin/bash\n')
ipt.append('\n')
ipt.append('/sbin/iptables -F\n')
ipt.append('/sbin/iptables -X\n\n')
for h in host_sp:
    if hostname.lower() == h[1].lower():
        #Начинаем обход организаций
        cur.execute(sql_select_all_org, (h[0], ))
        org_sp = cur.fetchall()
        for org in org_sp:
            # Генерируем правила для iptables
            ipt.append('#Org: ' + org[1] + '\n\n')
            ipt.append('\n')
            cur.execute(sql_select_users, (org[0],))
            vpn_users_sp = cur.fetchall()
            #Обход пользователей
            for vpn_user in vpn_users_sp:
                # iptables
                cur.execute(sql_select_allowips, (vpn_user[0],))
                allow_ips = cur.fetchall()
                ipt.append('/sbin/iptables -N ' + vpn_user[3] + '\n')
                ipt.append('/sbin/iptables -A FORWARD -s ' + vpn_user[1] + ' -j ' + vpn_user[3] + '\n')
                for allow_ip in allow_ips:
                    ipt.append('/sbin/iptables -A ' + vpn_user[3] + ' -d ' + allow_ip[0] + ' -j ACCEPT\n')
                ipt.append('/sbin/iptables -A ' + vpn_user[3] + ' -j DROP\n\n')
with codecs.open(ip_tables_name_file, 'w', encoding='UTF8') as f:
     for item in ipt:
         f.write("%s" % item)
     f.close()
#Заполняем файл конфигурации
for h in host_sp:
    if hostname.lower() == h[1].lower():
        #Начинаем обход организаций
        cur.execute(sql_select_org, (h[0], h[0]))
        org_sp = cur.fetchall()
        for org in org_sp:
            #ПРо
            name_wg_interface = prefix_wg_config+transliterate.translit(org[1], reversed=True)
            name_wg_interface_file = name_wg_interface + '.conf'
            name_wg_interface_new = name_wg_interface + '.new'
            name_wg_interface_new_file = name_wg_interface_new + '.conf'
            config_file_new = os.path.join(wireguard_patch, name_wg_interface_new_file)
            config_file_old = os.path.join(wireguard_patch, name_wg_interface_file)
            #Генерруем конфигурационный файл для wireguard
            conf = []
            conf.append('[Interface]\n')
            conf.append('Address = ' + org[6] + '\n')
            conf.append('ListenPort = ' + str(org[5])+'\n')
            conf.append('PrivateKey = ' + org[4]+'\n\n')
            cur.execute(sql_select_users, (org[0],))
            vpn_users_sp = cur.fetchall()
            #Обход пользователей
            for vpn_user in vpn_users_sp:
                conf.append('\n')
                conf.append('[Peer]\n')
                conf.append('PublicKey = ' + vpn_user[2]+'\n')
                conf.append('AllowedIPs = ' + vpn_user[1] + '\n')
            with codecs.open(name_wg_interface_new_file, 'w', encoding='UTF8') as f:
                for item in conf:
                    f.write("%s" % item)
            f.close()
            #Применяем правила фаервола
            os.system("/usr/bin/chmod +x " + ip_tables_name_file)
            os.system(ip_tables_name_file)
            # Протоколируем операцию
            try:
                cur.execute(sql_logged, ('Правила фаервола применены!',))
                conn.commit()
            except:
                print('Недоступен главный сервер БД')
            # перезаписываем файл в рабочий
            os.replace(config_file_new, config_file_old)
            #Обновляем rebuild config
            try:
                cur.execute(sql_update_rebuild, (h[0],))
                conn.commit()
            except:
                print('Недоступен главный сервер БД')
            #перезапускаем интерфейс systemctl restart wg-quick@wg_Avtosojuz
            os.system("/bin/systemctl restart wg-quick@" + name_wg_interface)
            # Протоколируем операцию
            try:
                cur.execute(sql_logged, ('Произведенно обновление конфигурационного файла для организации ' + org[1] + ' для хоста ' + h[1],))
                conn.commit()
            except:
                print('Недоступен главный сервер БД')



