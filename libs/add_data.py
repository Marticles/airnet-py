import datetime
import json
import pymysql
from libs.data_to_json import DateEncoder

def add_alarm(geopoint,pollution,value,email):
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='airnet', charset='utf8')
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_sql = 'INSERT INTO alarm VALUE (' + '\'' + nowtime + '\'' + ',' + '\'' + geopoint+ '\'' + ',' + '\'' + pollution + '\'' + ',' + '\'' + value + '\'' + ', ' + '\'' + email + '\'' + ')'
    cur.execute(insert_sql)
    conn.commit()
    cur.close()
    conn.close()
    return json.dumps({"msg":"添加成功"}, cls=DateEncoder)
