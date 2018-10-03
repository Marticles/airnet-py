from flask import Blueprint
from flask import render_template

web = Blueprint('web',__name__)

@web.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

from web import alarm
from web import api
from web import export
from web import forecast
from web import index
from web import other
from web import rank
from web import viz
from web import forecast