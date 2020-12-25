#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psycopg2
import os
import datetime
import transliterate
import codecs

wireguard_patch = '/etc/wireguard'
prefix_wg_config = 'wg_'
ip_tables_name_file = '/etc/wireguard/iptables.sh'
conn = psycopg2.connect(dbname='WireGuardUsers', user='flask', password='freud105b', host='localhost')
sql_select_rebuild = """select * from rebuild_config  order by last_update desc limit 1"""
sql_select_org = """select id_organizations, name_organizations, server_organizations, public_vpn_key_organizations, private_vpn_key_organizations, port, subnet from organizations """
sql_select_users = """select  id_vpn_users, adres_vpn, (select publickey from vpn_key where id_vpn_key=vpn_users.vpn_key) as p_key from vpn_users where active_vpn_users=true and organizations =  %s"""
sql_select_allowips = """select ip_allowedips||'/'||mask_allowedips from public.allowedips where vpn_user= %s"""
sql_update_rebuild = """update rebuild_config set rebuld=false"""
sql_logged = """insert into logging (user_id,descr) values (0,%s)"""
sql_filter_rules = """select * from iptables_rules where vpn_user = %s and active_rules=true"""
cur = conn.cursor()
cur.execute(sql_select_rebuild)
res = cur.fetchall()
WireGuard = os.path.abspath(wireguard_patch)
os.chdir(WireGuard)
if res[0][0]:
    #if True:
    #Начинаем обход организаций
    cur.execute(sql_select_org)
    org_sp = cur.fetchall()
    for org in org_sp:
        name_wg_interface = prefix_wg_config+transliterate.translit(org[1], reversed=True)
        name_wg_interface_file = name_wg_interface + '.conf'
        name_wg_interface_new = name_wg_interface + '.new'
        name_wg_interface_new_file = name_wg_interface_new + '.conf'
        config_file_new = os.path.join(wireguard_patch, name_wg_interface_new_file)
        config_file_old = os.path.join(wireguard_patch, name_wg_interface_file)

        #Генерруем конфигурационный файл для wireguard и iptables
        # Генерируем правила для iptables
        ipt = []
        ipt.append('#!/bin/bash\n')
        ipt.append('\n')
        ipt.append('iptables -F\n')
        ipt.append('iptables -X\n')
        ipt.append('\n')
        conf = []
        conf.append('[Interface]\n')
        conf.append('Address = ' + org[6] + '\n')
        conf.append('ListenPort = ' + str(org[5])+'\n')
        conf.append('PrivateKey = ' + org[4]+'\n')
        cur.execute(sql_select_users, (org[0],))
        vpn_users_sp = cur.fetchall()
        #Обход пользователей
        for vpn_user in vpn_users_sp:
            conf.append('\n')
            conf.append('[Peer]\n')
            conf.append('PublicKey = ' + vpn_user[2]+'\n')
            conf.append('AllowedIPs = ' + vpn_user[1] + '\n')
            #iptables
            cur.execute(sql_select_allowips,(vpn_user[0],))
            allow_ips = cur.fetchall()
            for allow_ip in allow_ips:
                ipt.append('iptable -A FORWARD -s '+ vpn_user[1] + ' -d ' + allow_ip[0]+' -j LOG --log-prefix peer '+str(vpn_user[0])+'\n')

        with codecs.open(name_wg_interface_new_file, 'w', encoding='UTF8') as f:
            for item in conf:
                f.write("%s" % item)
        f.close()
        print('ipt ', ipt)
        with codecs.open(ip_tables_name_file, 'w', encoding='UTF8') as f:
            for item in ipt:
                f.write("%s" % item)
        f.close()
        #Применяем правила фаервола
        os.system("/usr/bin/chmod +x " + ip_tables_name_file)
        os.system(ip_tables_name_file)
        # перезаписываем файл в рабочий
        os.replace(config_file_new, config_file_old)
        #Обновляем rebuild config
        cur.execute(sql_update_rebuild)
        conn.commit()
        #перезапускаем интерфейс
        #os.system("/usr/bin/wg-quick down " + name_wg_interface)
        #result = os.system("/usr/bin/wg-quick up " + name_wg_interface)
        # Протоколируем операцию
        cur.execute(sql_logged, ('Произведенно обновление конфигурационного файла !',))
        conn.commit()
        #print(result)


