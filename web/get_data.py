import pymysql
import datetime
import json
from lib.data_to_json import DateEncoder

def get_air_data():
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='airnet', charset='utf8')
    cur = conn.cursor()

    start_time = datetime.datetime.strptime('2018-04-25 00:01:00', "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime('2018-04-30 00:23:00', "%Y-%m-%d %H:%M:%S")

    sql = 'SELECT time, pm25 FROM hongkou WHERE time BETWEEN %s AND %s'
    cur.execute(sql, (start_time, end_time))
    data = cur.fetchall()

    json_data = {}
    time = []
    pm25 = []

    for single in data:
        time.append(single[0])
        pm25.append(single[1])

    json_data['time'] = time
    json_data['pm25'] = pm25
    j = json.dumps(json_data, cls=DateEncoder)

    cur.close()
    conn.close()
    return j

