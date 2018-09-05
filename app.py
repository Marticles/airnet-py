from flask import Flask, render_template
from web.get_data import get_air_data

app = Flask(__name__)

@app.route('/airdata',methods=['GET'])
def get_data():
    return (get_air_data())

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/linebarchart')
def linechart():

    return render_template('linebarchart.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
