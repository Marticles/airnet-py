import datetime
import json
import pymysql
from libs.data_to_json import DateEncoder
from web import secure

host = secure.DB_HOST
port = secure.DB_PORT
user = secure.DB_USERNAME
password = secure.DB_PASSWORD
db = secure.DB_NAME
charset = secure.DB_CHARSET

def add_alarm(geopoint,pollution,value,email):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_sql = 'INSERT INTO alarm VALUE (' + '\'' + nowtime + '\'' + ',' + '\'' + geopoint+ '\'' + ',' + '\'' + pollution + '\'' + ',' + '\'' + value + '\'' + ', ' + '\'' + email + '\'' + ')'
    cur.execute(insert_sql)
    conn.commit()
    cur.close()
    conn.close()
    return json.dumps({"msg":"添加成功"}, cls=DateEncoder)
