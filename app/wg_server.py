import psycopg2
import os
import datetime
import transliterate

wireguard_patch = '/etc/wireguard'
prefix_wg_config = 'wg_'

conn = psycopg2.connect(dbname='WireGuardUsers', user='flask', password='freud105b', host='localhost')
sql_select_rebuild = """select * from rebuild_config  order by last_update desc limit 1"""
sql_select_org = """select * from organizations """

cur = conn.cursor()
cur.execute(sql_select_rebuild)
res = cur.fetchall()
print(res[0][0])
if res[0][0]:
    print('Данные обновились начинаем обработку')
    #Начинаем обход организаций
    cur.execute(sql_select_org)
    org_sp = cur.fetchall()
    for org in org_sp:
        print(org)
        name_wg_interface = prefix_wg_config+transliterate.translit(org[1], reversed=True)
        print('name_wg_interface', name_wg_interface)
        # проверяем существует ли конфигурационный файл для данной организации
        config_file = os.path.join(wireguard_patch,name_wg_interface)
        if os.path.exists(config_file):
            print('Файл существует. удаляем его')
            os.remove(config_file)

else:
    print('Ничего не делаем')
