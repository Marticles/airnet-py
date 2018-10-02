from . import web
from flask import render_template

@web.route('/aboutapi')
def aboutapi():
    return render_template('aboutapi.html')

@web.route('/info')
def info():
    return render_template('info.html')

@web.route('/about')
def about():
    return render_template('about.html')

