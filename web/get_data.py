import pymysql
import datetime
import json
from lib.data_to_json import DateEncoder


def get_air_data(start_time='2018-04-21 01:00:00', end_time='2018-04-25 02:00:00', pollution='pm25',
                 geopoint='yangpusipiao'):
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='airnet', charset='utf8')
    cur = conn.cursor()

    if (isinstance(start_time, str) and isinstance(end_time, str)):
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    sql_default = 'SELECT time, `{0}` FROM `{1}` WHERE time BETWEEN %s AND %s'
    sql = 'SELECT time, pm25,pm10,co,no2,ozone1hour,ozone8hour,so2,aqi,level,primarypollutant FROM `{0}` WHERE time BETWEEN %s AND %s'

    if (pollution != 'pm25'):
        cur.execute(sql.format(geopoint), (start_time, end_time))
        data = cur.fetchall()
        json_data = {}
        time = []
        pollution = {}
        aqi = []
        pm25 = []
        pm10 = []
        co = []
        no2 = []
        ozone1hour = []
        ozone8hour = []
        so2 = []
        level = []
        primarypollutant = []

        for single in data:
            time.append(single[0])
            pm25.append(single[1])
            pm10.append(single[2])
            co.append(single[3])
            no2.append(single[4])
            ozone1hour.append(single[5])
            ozone8hour.append(single[6])
            so2.append(single[7])
            aqi.append(single[8])
            level.append(single[9])
            primarypollutant.append(single[10])

        pollution['pm25'] = pm25
        pollution['pm10'] = pm10
        pollution['co'] = co
        pollution['no2'] = no2
        pollution['ozone1hour'] = ozone1hour
        pollution['ozone8hour'] = ozone8hour
        pollution['so2'] = so2
        pollution['aqi'] = aqi
        pollution['level'] = level
        pollution['primarypollutant'] = primarypollutant

        json_data['time'] = time
        json_data['pollution'] = pollution
        air_json = json.dumps(json_data, cls=DateEncoder)

        cur.close()
        conn.close()

        return (air_json)

    else:
        cur.execute(sql_default.format(pollution, geopoint), (start_time, end_time))
        data = cur.fetchall()
        json_data = {}
        time = []
        pollution = []

        for single in data:
            time.append(single[0])
            pollution.append(single[1])
        json_data['time'] = time
        json_data['pm25'] = pollution
        air_json = json.dumps(json_data, cls=DateEncoder)
        cur.close()
        conn.close()
        return (air_json)


def datatime_converter(object):
    if isinstance(object, datetime.datetime):
        return object.__str__()
