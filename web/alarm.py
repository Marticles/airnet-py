from . import web
from flask import request, render_template
from libs.add_data import *
from libs.del_data import *
from libs.email import *
import datetime

@web.route('/alarm')
def alarm():
    return render_template('alarm.html')

@web.route('/alarminfo', methods=['GET'])
def alarminfo():
    if request.method == 'GET':
        return get_alarminfo(True)


@web.route('/addalarm', methods=['POST'])
def addalarm():
    if request.method == 'POST':
        geopoint = request.get_json()['geopoint']
        pollution = request.get_json()['pollution']
        value = request.get_json()['value']
        email = request.get_json()['email']
        return add_alarm(geopoint, pollution, value, email)


@web.route('/delalarm', methods=['POST'])
def delalarm():
    if request.method == 'POST':
        index_time = request.get_json().replace("T", " ")
        index_time = index_time.replace(".000Z", "")
        index_time = datetime.datetime.strptime(index_time, "%Y-%m-%d %H:%M:%S")
        index_time.replace(minute=0, second=0)
        return del_alarm(index_time)
