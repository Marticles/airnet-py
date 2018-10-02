from . import web
from flask import request, render_template
from libs.get_data import *
from libs.format_time import format_time
from web.cache import cache

@web.route('/indexdata', methods=['POST'])
@cache.cached(timeout=60*30)
def get_indexdata():
    if request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = format_time(start_time)
        pollution = request.get_json()['pollution']
        return get_index_data(start_time, pollution)

@web.route('/lastdate', methods=['GET'])
@cache.cached(timeout=60*30)
def get_lastdate():
    if request.method == 'GET':
        return (get_index_lastdate())

@web.route('/')
@cache.cached(timeout=60*30)
def index():
    return render_template('index.html')
