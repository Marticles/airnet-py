import datetime
import json
import pymysql
from libs.data_to_json import DateEncoder

def del_alarm(index_time):
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='airnet', charset='utf8')
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    index_time = index_time.strftime("%Y-%m-%d %H:%M:%S")
    del_sql = 'delete from alarm where time= ' + '\'' + index_time + '\''
    cur.execute(del_sql)
    conn.commit()
    cur.close()
    conn.close()
    return json.dumps({"msg":"删除成功"}, cls=DateEncoder)
