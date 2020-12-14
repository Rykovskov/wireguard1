# -*- coding: utf-8 -*-
import psycopg2
import os
import datetime
import transliterate

wireguard_patch = '/etc/wireguard'
prefix_wg_config = 'wg_'

conn = psycopg2.connect(dbname='WireGuardUsers', user='flask', password='freud105b', host='localhost')
sql_select_rebuild = """select * from rebuild_config  order by last_update desc limit 1"""
sql_select_org = """select * from organizations """
sql_select_users = """select  id_vpn_users, (select publickey from vpn_key where id_vpn_key=vpn_users.vpn_key) as p_key from vpn_users where active_vpn_users=true and organizations =  %s"""
sql_select_allowips = """select * from allowedips where vpn_user = %s"""
sql_update_rebuild = """update rebuild_config set rebuld=false"""
cur = conn.cursor()
cur.execute(sql_select_rebuild)
res = cur.fetchall()
WireGuard = os.path.abspath(wireguard_patch)
os.chdir(WireGuard)
if res[0][0]:
    print('Данные обновились начинаем обработку')
    #Начинаем обход организаций
    cur.execute(sql_select_org)
    org_sp = cur.fetchall()
    for org in org_sp:
        print(org)
        name_wg_interface = prefix_wg_config+transliterate.translit(org[1], reversed=True)
        name_wg_interface_file = name_wg_interface + '.conf'
        name_wg_interface_new = name_wg_interface + '.new'
        name_wg_interface_new_file = name_wg_interface_new + '.conf'
        config_file_new = os.path.join(wireguard_patch, name_wg_interface_new_file)
        config_file_old = os.path.join(wireguard_patch, name_wg_interface_file)
        f = open(name_wg_interface_new_file, 'w')
        #Генерруем конфигурационный файл
        conf = []
        conf.append('[Interface]')
        conf.append('PrivateKey = ' + org[3])
        conf.append('ListenPort = ' + str(org[5]))
        cur.execute(sql_select_users, (org[0],))
        vpn_users_sp = cur.fetchall()
        #Обход пользователей
        for vpn_user in vpn_users_sp:
            conf.append('')
            conf.append('[Peer]')
            conf.append('PublicKey = ' + vpn_user[1])
            #Получаем список разрешенных подсетей
            al_ip = 'AllowedIPs = '
            cur.execute(sql_select_allowips, (vpn_user[0],))
            sp_allowed_ips = cur.fetchall()
            for alliwed_ip in sp_allowed_ips:
                al_ip = al_ip + alliwed_ip[1]+'/'+alliwed_ip[2]+', '
            al_ip = al_ip[:-1]
            conf.append(al_ip)
        for item in conf:
            f.write("%s\n" % item)
        f.close()
        # перезаписываем файл в рабочий
        os.replace(config_file_new, config_file_old)
        #Обновляем rebuild config
        cur.execute(sql_update_rebuild)
        conn.commit()
        #перезапускаем интерфейс
        os.system("/usr/bin/wg-quick down " + name_wg_interface)
        os.system("/usr/bin/wg-quick down " + name_wg_interface)


