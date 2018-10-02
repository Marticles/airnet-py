from . import web
from flask import render_template, request
from libs.get_data import *
from libs.format_time import format_time

@web.route('/rank')
def rank():
    return render_template('rank.html')

@web.route('/ranknowdata', methods=['GET'])
def get_ranknowdata():
    if request.method == 'GET':
        return get_rank_now_data()

@web.route('/rankhistorydata', methods=['POST'])
def get_rankhistorydata():
    if request.method == 'POST':
        start_time = request.get_json()['start'].replace("T", " ")
        start_time = format_time(start_time)
        order = request.get_json()['order']
        return get_rank_history_data(start_time, order)


