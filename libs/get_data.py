import datetime
import json
import pandas as pd
import pymysql
from libs.data_to_json import DateEncoder
from web import secure

host = secure.DB_HOST
port = secure.DB_PORT
user = secure.DB_USERNAME
password = secure.DB_PASSWORD
db = secure.DB_NAME
charset = secure.DB_CHARSET


def get_air_data(start_time='2018-04-21 01:00:00', end_time='2018-04-25 02:00:00', pollution='pm25',
                 geopoint='yangpusipiao'):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor()

    if (isinstance(start_time, str) and isinstance(end_time, str)):
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    sql_default = 'SELECT time, `{0}` FROM `{1}` WHERE time BETWEEN %s AND %s'
    sql = 'SELECT time, pm25,pm10,co,no2,ozone1hour,ozone8hour,so2,aqi,level,primarypollutant FROM `{0}` WHERE time BETWEEN %s AND %s'

    if (pollution == 'pm25'):
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

    else:
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


def get_index_data(start_time='2018-03-25 12:00:00', pollution='pm25'):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor()
    if (isinstance(start_time, str)):
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    sql = 'select time,aqi,`{0}` from hongkou WHERE time = %s ' \
          'union all select time,aqi,`{1}` from jingan WHERE time = %s ' \
          'union all select time,aqi,`{2}` from pudongchuansha WHERE time = %s' \
          'union all select time,aqi,`{3}` from pudongxinqu WHERE time = %s' \
          'union all select time,aqi,`{4}` from pudongzhangjiang WHERE time = %s' \
          'union all select time,aqi,`{5}` from putuo WHERE time = %s' \
          'union all select time,aqi,`{6}` from qingpudianshanhu WHERE time = %s' \
          'union all select time,aqi,`{7}` from shiwuchang WHERE time = %s' \
          'union all select time,aqi,`{8}` from xuhuishangshida WHERE time = %s' \
          'union all select time,aqi,`{9}` from yangpusipiao WHERE time = %s'
    cur.execute(
        sql.format(pollution, pollution, pollution, pollution, pollution, pollution, pollution, pollution, pollution,
                   pollution), (
            start_time, start_time, start_time, start_time, start_time, start_time, start_time, start_time, start_time,
            start_time))
    data = cur.fetchall()
    json_data = {}
    time = []
    hongkou_aqi = [];
    hongkou_pollution = []
    jingan_aqi = [];
    jingan_pollution = []
    geo = (
        'hongkou', 'jingan', 'pudongchuansha', 'pudongxinqu', 'pudongzhangjiang', 'putuo', 'qingpudianshanhu',
        'shiwuchang',
        'xuhuishangshida', 'yangpusipiao')
    for x, v in zip(geo, data):
        json_data[x] = v

    index_json = json.dumps(json_data, cls=DateEncoder)
    cur.close()
    conn.close()
    return (index_json)


def get_index_lastdate(type):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor()
    sql = 'select time from yangpusipiao order by time desc limit 1'
    cur.execute(sql)
    lastdate = cur.fetchall()
    json_lastdate = {}
    json_lastdate['lasttime'] = lastdate
    json_lastdate = json.dumps(json_lastdate, cls=DateEncoder)
    cur.close()
    conn.close()
    if type =="time":
        return (json_lastdate)
    if type =="site":
        return list(lastdate)



def get_rank_now_data():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = '(select * from hongkou order by time desc limit 1 )' \
          'union all (select * from jingan order by time desc limit 1 )' \
          'union all (select * from pudongchuansha order by time desc limit 1)' \
          'union all (select * from pudongxinqu order by time desc limit 1)' \
          'union all (select * from pudongzhangjiang order by time desc limit 1)' \
          'union all (select * from putuo order by time desc limit 1)' \
          'union all (select * from qingpudianshanhu order by time desc limit 1)' \
          'union all (select * from shiwuchang order by time desc limit 1)' \
          'union all (select * from xuhuishangshida order by time desc limit 1)' \
          'union all (select * from yangpusipiao order by time desc limit 1)' \
          'order by aqi'
    cur.execute(sql)
    rankdata = cur.fetchall()

    json_rankdata = {}
    # geo = (
    #      'hongkou','jingan', 'pudongchuansha', 'pudongxinqu', 'pudongzhangjiang', 'putuo', 'qingpudianshanhu',
    #     'shiwuchang',
    #     'xuhuishangshida', 'yangpusipiao')
    # for x, v in zip(geo, rankdata):
    #     json_rankdata[x] = v

    json_rankdata = json.dumps(rankdata, cls=DateEncoder)
    cur.close()
    conn.close()
    return (json_rankdata)


def get_rank_history_data(start_time, order):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    order_sql = 'aqi'
    if order == 'order':
        pass
    elif order == 'reverse':
        order_sql = 'aqi desc'

    sql = '(select * from hongkou WHERE time = %s )' \
          'union all (select * from jingan WHERE time = %s )' \
          'union all (select * from pudongchuansha WHERE time = %s)' \
          'union all (select * from pudongxinqu WHERE time = %s)' \
          'union all (select * from pudongzhangjiang WHERE time = %s)' \
          'union all (select * from putuo WHERE time = %s)' \
          'union all (select * from qingpudianshanhu WHERE time = %s)' \
          'union all (select * from shiwuchang WHERE time = %s)' \
          'union all (select * from xuhuishangshida WHERE time = %s)' \
          'union all (select * from yangpusipiao WHERE time = %s)' \
          'order by ' + order_sql

    cur.execute(sql, (
        start_time, start_time, start_time, start_time, start_time, start_time, start_time, start_time, start_time,
        start_time))
    rankdata = cur.fetchall()
    json_rankdata = json.dumps(rankdata, cls=DateEncoder)
    cur.close()
    conn.close()
    return (json_rankdata)


def get_export_data(start_time, end_time, geopoint):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = 'SELECT * FROM ' + geopoint + ' WHERE time BETWEEN ' + '\'' + start_time + '\'' + ' AND ' + '\'' + end_time + '\''
    df = pd.read_sql(sql, con=conn)
    csv_name = 'export/' + geopoint + '-' + start_time.replace(' ', '-').replace(':', '-') + '-' + end_time.replace(' ',
                                                                                                                    '-').replace(
        ':', '-') + '.csv'
    df.to_csv(csv_name,encoding='utf_8_sig')
    new_csv_name = csv_name.replace('export/', '')
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    insert_sql = 'INSERT INTO export VALUE (' + '\'' + nowtime + '\'' + ',' + '\'' + start_time + '\'' + ',' + '\'' + end_time + '\'' + ',' + '\'' + geopoint + '\'' + ', ' + '\'' + new_csv_name + '\'' + ')'
    cur.execute(insert_sql)
    conn.commit()
    cur.close()
    conn.close()

    return json.dumps(new_csv_name, cls=DateEncoder)


def get_downloadinfo():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = 'select * from export order by time desc;'
    cur.execute(sql)
    downloadinfo = cur.fetchall()
    json_downloadinfo = json.dumps(downloadinfo, cls=DateEncoder)
    cur.close()
    conn.close()
    return json_downloadinfo


def get_alarminfo(jsonify):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = 'select * from alarm order by time desc;'
    cur.execute(sql)
    alarminfo = cur.fetchall()
    json_alarminfo = json.dumps(alarminfo, cls=DateEncoder)
    cur.close()
    conn.close()
    if jsonify == True:
        return json_alarminfo
    elif jsonify == False:
        return alarminfo


def check_alarm(site, pollution, value):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor()
    sql = 'select time,' + pollution + ' from ' + site + ' order by time desc limit 1;'
    cur.execute(sql)
    check_info = cur.fetchall()
    if (float(check_info[0][1]) >= float(value)):
        return {"state": True, "db_value": check_info[0][1], "db_time": check_info[0][0]}
    elif (float(check_info[0][1]) < float(value)):
        return {"state": False, "db_value": check_info[0][1], "db_time": check_info[0][0]}


def get_api_history(site, pollution, start_time, end_time):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    if (pollution == 'all'):
        sql = 'select * from ' + site + ' where time between ' + '\'' + start_time + '\'' + ' and ' + '\'' + end_time + '\''
    else :
        sql = 'select time, ' + pollution + ' from ' + site + ' where time between ' + '\'' + start_time + '\'' + ' and ' + '\'' + end_time + '\''
    cur.execute(sql)
    api_history_info = cur.fetchall()
    json_api_history_info = {}
    json_api_history_info['request_site']= site
    json_api_history_info['data'] = api_history_info
    cur.close()
    conn.close()
    return json.dumps(json_api_history_info, cls=DateEncoder,ensure_ascii=False)

def get_api_forecast(site, start_time, end_time):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = 'select time, forecast_pm25 from ' +'forecast_'+site + ' where time between ' + '\'' + start_time + '\'' + ' and ' + '\'' + end_time + '\''
    cur.execute(sql)
    api_forecast_info = cur.fetchall()
    api_forecast_json = {}
    api_forecast_json['request_site'] = site
    api_forecast_json['data'] = api_forecast_info
    cur.close()
    conn.close()
    return json.dumps(api_forecast_json, cls=DateEncoder,ensure_ascii=False)

def get_api_lastest(site, pollution):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    if (pollution == 'all'):
        sql = 'select * from ' + site + ' order by time desc limit 1'
    else :
        sql = 'select time, ' + pollution + ' from ' + site + ' order by time desc limit 1'
    cur.execute(sql)
    api_lastest_info = cur.fetchall()
    json_api_lastest_info = {}
    json_api_lastest_info['request_site'] = site
    json_api_lastest_info['data'] = api_lastest_info
    cur.close()
    conn.close()
    return json.dumps(json_api_lastest_info, cls=DateEncoder,ensure_ascii=False)

def get_forecast_default():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    # 24hours * 7 days = 168 hours
    sql = 'select time, forecast_pm25 from  forecast_yangpusipiao order by time asc limit 168 '
    cur.execute(sql)
    forecast_default = cur.fetchall()
    forecast_default_json = {}
    time = []
    forecast_pm25 = []

    for single in forecast_default:
        time.append(single['time'])
        forecast_pm25.append(single['forecast_pm25'])

    forecast_default_json['time'] = time
    forecast_default_json['forecast_pm25'] = forecast_pm25
    cur.close()
    conn.close()
    return json.dumps(forecast_default_json, cls=DateEncoder)

def get_forecast_data(start_time,forecast_day,geopoint):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset=charset)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    forecast_day = int(forecast_day)*24
    sql = 'select time, forecast_pm25 from  forecast_'+geopoint+' order by time asc limit ' + str(forecast_day)
    cur.execute(sql)
    forecast_data = cur.fetchall()
    cur.execute('select time from ' + geopoint + ' order by time desc limit 1')
    last_date = cur.fetchall()
    sql = 'select time, pm25 from '+geopoint+' where time between %s and %s'
    cur.execute(sql,(start_time,last_date[0]['time']))
    real_data = cur.fetchall()
    forecast_real_json = {}
    forecast_time = []
    forecast_pm25 = []
    real_time = []
    real_pm25 = []
    for single in forecast_data:
        forecast_time.append(single['time'])
        forecast_pm25.append(single['forecast_pm25'])
    for single in real_data:
        real_time.append(single['time'])
        real_pm25.append(single['pm25'])

    forecast_real_json['forecast_time'] = forecast_time
    forecast_real_json['forecast_pm25'] = forecast_pm25
    forecast_real_json['real_time'] = real_time
    forecast_real_json['real_pm25'] = real_pm25

    cur.close()
    conn.close()
    return json.dumps(forecast_real_json, cls=DateEncoder)


def datatime_converter(object):
    if isinstance(object, datetime.datetime):
        return object.__str__()
