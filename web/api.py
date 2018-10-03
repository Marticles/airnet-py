from . import web
from flask import request
from libs.get_data import *

@web.route('/api/history/<site>/<pollution>', methods=['GET'])
def api_history(site, pollution):
    start, end = request.args.get('start'), request.args.get('end')
    return get_api_history(site, pollution, start, end)

@web.route('/api/forecast/<site>', methods=['GET'])
def api_forecast(site):
    start, end = request.args.get('start'), request.args.get('end')
    return get_api_forecast(site, start, end)

@web.route('/api/lastest/<site>/<pollution>', methods=['GET'])
def api_lastest(site, pollution):
    return get_api_lastest(site, pollution)
