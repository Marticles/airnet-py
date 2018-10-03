from . import web
from flask import send_from_directory, make_response, request, render_template
from libs.get_data import *
import os

@web.route('/export')
def export():
    return render_template('export.html')

@web.route('/exportdata', methods=['POST'])
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


@web.route('/download/<filename>', methods=['GET'])
def download(filename):
    directory = os.getcwd()
    response = make_response(send_from_directory(directory + '/export', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        filename.encode('utf-8').decode('utf-8'))
    return response


@web.route('/downloadinfo', methods=['GET'])
def downloadinfo():
    if request.method == 'GET':
        return get_downloadinfo()
