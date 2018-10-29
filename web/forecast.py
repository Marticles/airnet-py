from . import web
from flask import request, render_template
from libs.get_data import get_forecast_default, get_forecast_data
from libs.format_time import format_time
import os
import json
import time
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(5)

@web.route('/forecast')
def forecast():
    return render_template('forecast.html')


@web.route('/forecast_pm25', methods=['POST', 'GET', 'PUT'])
def forecast_pm25():
    if request.method == 'GET':
        return get_forecast_default()
    elif request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = format_time(start_time)
        geopoint = request.get_json()['geopoint']
        forecast_day = request.get_json()['forecast_day']
        return get_forecast_data(start_time, forecast_day, geopoint)
    elif request.method == 'PUT':
        days = request.get_json()['days']
        geopoint = request.get_json()['geopoint']
        path = ('/home/AirNet/libs/forecast_pm25.py ' + geopoint + ' train ' + str(days))
        executor.submit(run_forecast(geopoint, days))
        return (json.dumps("后台任务已加入！"))


def run_forecast(geopoint, days):
    path = ('~/test/forecast_pm25.py ' + geopoint + ' train ' + str(days))
    status = os.system(path)
