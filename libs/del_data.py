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

def del_alarm(index_time):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    index_time = index_time.strftime("%Y-%m-%d %H:%M:%S")
    del_sql = 'delete from alarm where time= ' + '\'' + index_time + '\''
    cur.execute(del_sql)
    conn.commit()
    cur.close()
    conn.close()
    return json.dumps({"msg":"删除成功"}, cls=DateEncoder)
