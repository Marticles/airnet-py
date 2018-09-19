from flask import Flask, render_template, send_file, send_from_directory, make_response, request
from flask_apscheduler import APScheduler
from web.get_data import *
from web.add_data import *
from web.del_data import *
from lib.email import send_async_email, send_email
from lib.format_time import format_time
import datetime
import os
import json


class Config(object):
    JOBS = []


app = Flask(__name__)
app.config.from_object(Config())
app.config.from_object('secure')
scheduler = APScheduler();
scheduler.init_app(app=app)
scheduler.start()


# scheduler.add_job(func=send_email, id='send_email', args=(), trigger='interval', seconds=60, replace_existing=True)

@app.route('/test', methods=['GET'])
def test():
    return 0

@app.route('/api/history/<site>/<pollution>', methods=['GET'])
def api_history(site, pollution):
    start, end = request.args.get('start'), request.args.get('end')
    return get_api_history(site, pollution, start, end)

@app.route('/api/forecast/<site>/<pollution>', methods=['GET'])
def api_forecast(site, pollution):
    start, end = request.args.get('start'), request.args.get('end')
    return get_api_forecast(site, pollution, start, end)


@app.route('/api/lastest/<site>/<pollution>', methods=['GET'])
def api_lastest(site, pollution):
    return get_api_lastest(site, pollution)

@app.route('/vizdata', methods=['POST', 'GET'])
def get_data():
    if request.method == 'GET':
        return (get_air_data())
    elif request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = start_time.replace(".000Z", "")
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        start_time += datetime.timedelta(hours=+8)
        start_time.replace(minute=0, second=0)
        end_time = request.get_json()['end'].replace("T", " ")
        end_time = end_time.replace(".000Z", "")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        end_time += datetime.timedelta(hours=+8)
        end_time.replace(minute=0, second=0)
        pollution = request.get_json()['pollution']
        geopoint = request.get_json()['geopoint']
        return get_air_data(start_time, end_time, pollution, geopoint)


@app.route('/indexdata', methods=['POST'])
def get_indexdata():
    if request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = start_time.replace(".000Z", "")
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        start_time += datetime.timedelta(hours=+8)
        start_time.replace(minute=0, second=0)
        pollution = request.get_json()['pollution']
        return get_index_data(start_time, pollution)


@app.route('/lastdate', methods=['GET'])
def get_lastdate():
    if request.method == 'GET':
        return (get_index_lastdate())


@app.route('/ranknowdata', methods=['GET'])
def get_ranknowdata():
    if request.method == 'GET':
        return get_rank_now_data()


@app.route('/rankhistorydata', methods=['POST'])
def get_rankhistorydata():
    if request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = start_time.replace(".000Z", "")
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        start_time += datetime.timedelta(hours=+8)
        start_time.replace(minute=0, second=0)
        order = request.get_json()['order']
        return get_rank_history_data(start_time, order)


@app.route('/exportdata', methods=['POST'])
def get_exportdata():
    if request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = start_time.replace(".000Z", "")
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        start_time += datetime.timedelta(hours=+8)
        start_time.replace(minute=0, second=0)
        end_time = request.get_json()['end'].replace("T", " ")
        end_time = end_time.replace(".000Z", "")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        end_time += datetime.timedelta(hours=+8)
        end_time.replace(minute=0, second=0)
        geopoint = request.get_json()['geopoint']
        return get_export_data(start_time, end_time, geopoint)


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    directory = os.getcwd()
    response = make_response(send_from_directory(directory + '/export', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        filename.encode('utf-8').decode('utf-8'))
    return response


@app.route('/downloadinfo', methods=['GET'])
def downloadinfo():
    if request.method == 'GET':
        return get_downloadinfo()


@app.route('/alarminfo', methods=['GET'])
def alarminfo():
    if request.method == 'GET':
        return get_alarminfo(True)


@app.route('/addalarm', methods=['POST'])
def addalarm():
    if request.method == 'POST':
        geopoint = request.get_json()['geopoint']
        pollution = request.get_json()['pollution']
        value = request.get_json()['value']
        email = request.get_json()['email']
        return add_alarm(geopoint, pollution, value, email)


@app.route('/delalarm', methods=['POST'])
def delalarm():
    if request.method == 'POST':
        index_time = request.get_json().replace("T", " ")
        index_time = index_time.replace(".000Z", "")
        index_time = datetime.datetime.strptime(index_time, "%Y-%m-%d %H:%M:%S")
        index_time.replace(minute=0, second=0)
        return del_alarm(index_time)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/viz/line')
def line():
    return render_template('line.html')


@app.route('/viz/bar')
def bar():
    return render_template('bar.html')


@app.route('/viz/scatter')
def scatter():
    return render_template('scatter.html')


@app.route('/viz/pie')
def pie():
    return render_template('pie.html')


@app.route('/viz/rose')
def rose():
    return render_template('rose.html')


@app.route('/viz/radar')
def radar():
    return render_template('radar.html')


@app.route('/viz/funnel')
def funnel():
    return render_template('funnel.html')


@app.route('/rank')
def rank():
    return render_template('rank.html')


@app.route('/export')
def export():
    return render_template('export.html')


@app.route('/alarm')
def alarm():
    return render_template('alarm.html')


@app.route('/aboutapi')
def aboutapi():
    return render_template('aboutapi.html')


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
