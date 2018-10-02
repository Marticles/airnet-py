from . import web
from flask import render_template, request
from libs.get_data import *
from libs.format_time import format_time

@web.route('/vizdata', methods=['POST', 'GET'])
def get_data():
    if request.method == 'GET':
        return (get_air_data())
    elif request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = format_time(start_time)
        end_time = request.get_json()['end'].replace("T", " ")
        start_time = format_time(start_time)
        pollution = request.get_json()['pollution']
        geopoint = request.get_json()['geopoint']
        return get_air_data(start_time, end_time, pollution, geopoint)

@web.route('/viz/line')
def line():
    return render_template('line.html')

@web.route('/viz/bar')
def bar():
    return render_template('bar.html')

@web.route('/viz/scatter')
def scatter():
    return render_template('scatter.html')

@web.route('/viz/pie')
def pie():
    return render_template('pie.html')

@web.route('/viz/rose')
def rose():
    return render_template('rose.html')

@web.route('/viz/radar')
def radar():
    return render_template('radar.html')

@web.route('/viz/funnel')
def funnel():
    return render_template('funnel.html')
