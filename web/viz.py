from . import web
from flask import render_template, request
from libs.get_data import *
from libs.format_time import format_time
from web.cache import cache

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
@cache.cached(timeout=60*30)
def line():
    return render_template('line.html')

@web.route('/viz/bar')
@cache.cached(timeout=60*30)
def bar():
    return render_template('bar.html')

@web.route('/viz/scatter')
@cache.cached(timeout=60*30)
def scatter():
    return render_template('scatter.html')

@web.route('/viz/pie')
@cache.cached(timeout=60*30)
def pie():
    return render_template('pie.html')

@web.route('/viz/rose')
@cache.cached(timeout=60*30)
def rose():
    return render_template('rose.html')

@web.route('/viz/radar')
@cache.cached(timeout=60*30)
def radar():
    return render_template('radar.html')

@web.route('/viz/funnel')
@cache.cached(timeout=60*30)
def funnel():
    return render_template('funnel.html')
