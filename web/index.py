from . import web
from flask import request, render_template
from libs.get_data import *
from libs.format_time import format_time
from web.cache import cache
import datetime

@web.route('/indexdata', methods=['POST'])
def get_indexdata():
    if request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = format_time(start_time)
        print(start_time)
        pollution = request.get_json()['pollution']
        return get_index_data(start_time, pollution)

@web.route('/lastdate', methods=['GET','POST'])
def get_lastdate():
    if request.method == 'GET':
        return (get_index_lastdate("time"))
    else:
        time = get_index_lastdate("site")
        return get_index_data(time[0][0],"pm25")


@web.route('/')
def index():
    return render_template('index.html')
