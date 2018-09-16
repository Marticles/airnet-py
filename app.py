from flask import Flask, render_template,send_file, send_from_directory,make_response
from web.get_data import get_air_data, get_index_data,get_index_lastdate,get_rank_now_data,get_rank_history_data,get_export_data
from flask import request
import datetime
import os

app = Flask(__name__)


@app.route('/airdata', methods=['POST', 'GET'])
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
        return (get_air_data(start_time, end_time, pollution, geopoint))


@app.route('/indexdata', methods=['POST'])
def get_indexdata():
    if request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = start_time.replace(".000Z", "")
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        start_time += datetime.timedelta(hours=+8)
        start_time.replace(minute=0, second=0)
        pollution = request.get_json()['pollution']
        return (get_index_data(start_time, pollution))


@app.route('/lastdate', methods=['GET'])
def get_lastdate():
    if request.method == 'GET':
        return (get_index_lastdate())

@app.route('/ranknowdata', methods=['GET'])
def get_ranknowdata():
    if request.method == 'GET':
        return (get_rank_now_data())

@app.route('/rankhistorydata', methods=['POST'])
def get_rankhistorydata():
    if request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = start_time.replace(".000Z", "")
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        start_time += datetime.timedelta(hours=+8)
        start_time.replace(minute=0, second=0)
        order = request.get_json()['order']
        return (get_rank_history_data(start_time,order))

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
        return (get_export_data(start_time,end_time,geopoint))

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    directory = os.getcwd()
    response = make_response(send_from_directory(directory+'/export', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        filename.encode('utf-8').decode('utf-8'))
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    return render_template('test.html')


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
