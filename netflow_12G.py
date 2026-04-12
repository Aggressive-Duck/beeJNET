from datetime import date, datetime, timedelta
from time import time, sleep
from io import BytesIO

import schedule
from pymysql import connect as sqlconnect
from lxml import etree
import requests

buffer = BytesIO()

credentials = {
    "user": "netflow",
    "password": "FullAutoNetFlow",
    "db": "YunNet"
}

def updateNetFlow():
    conn = sqlconnect(**credentials)
    today = date.today()
    print(today)
    url = "https://netflow.yuntech.edu.tw/netflow.pl?year={0}&month={1}&day={2}&number=200".format(today.year, today.month, today.day)
    res = requests.get(url, verify=False)
    parser = etree.HTMLParser(encoding="big5")
    print("Parsing...")
    root = etree.fromstring(res.content, parser=parser)
    print("Grabbing...")
    result = root.findall(".//tr[@bgcolor='#ffffbb']")
    print("Inserting...")
    bed_ip = {}
    bed_ip_list = []
    with conn.cursor() as cur:
        cur.execute("SELECT `ip`, `uid`, `gid` FROM `iptable` WHERE `ip_type_id` BETWEEN 1 AND 2 AND `is_unlimited` = 0 AND `lock_id` IS NULL")
        bed_ip_result = cur.fetchall()
        for ip in bed_ip_result:
            obj = {
                ip[0]: {
                    "uid": ip[1],
                    "gid": ip[2],
                }
            }
            bed_ip.update(obj)
            bed_ip_list.append(ip[0])
    lock_count = 0
    for row in result:
        IP = row[1][0].text
        
        wan_upload = int(row[2].text.strip().replace(".",""))
        wan_download = int(row[3].text.strip().replace(".",""))
        lan_upload = int(row[4].text.strip().replace(".",""))
        lan_download = int(row[5].text.strip().replace(".",""))
        if IP in bed_ip:
            GB = wan_upload + wan_download
            GB = GB / 1024 / 1024
            if GB > 15:
                lock_count += 1
                print("{0}, {1}".format(IP, GB))
                
                unlock_date = today + timedelta(days=1)
                 
                para_input = [ IP, bed_ip[IP]["uid"], bed_ip[IP]["gid"], unlock_date, GB]
                with conn.cursor() as cur:
                    sql = (
                        "INSERT INTO `lock` "
                        "(`lock_type_id`, `ip`, `uid`, `gid`, `lock_date`, "
                        "`unlock_date`, `title`, `description`, `lock_by_user_id`) "
                        "VALUES ('1', %s,  %s, %s, CURRENT_TIME(), %s, 'Overflow', %s, NULL)"
                    )
                    cur.execute(sql, para_input)
                    ip_lock_sql = (
                        "UPDATE `iptable` SET `lock_id` = %s WHERE `iptable`.`ip` = %s"
                    )
                    cur.execute(ip_lock_sql, [cur.lastrowid, IP])
                    ip_update_sql = (
                        "UPDATE `iptable` SET `is_updated` = 0 WHERE `iptable`.`ip` = %s"
                    )
                    cur.execute(ip_update_sql, IP)
    print("Committing changes...")       
    conn.commit()
    print("Locked {0} IP".format(lock_count))
    del(root)
    del(result)

schedule.every().hour.at(":20").do(updateNetFlow)

updateNetFlow()
while True:
    schedule.run_pending()
    sleep(1)