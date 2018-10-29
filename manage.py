from flask import Flask
from flask_apscheduler import APScheduler
from web.cache import cache
from libs.email import send_email
import config


class Config(object):
    JOBS = []
    CACHE_TYPE = config.CACHE_TYPE
    CACHE_REDIS_HOST = config.CACHE_REDIS_HOST
    CACHE_REDIS_PORT = config.CACHE_REDIS_PORT
    CACHE_REDIS_DB = config.CACHE_REDIS_DB
    CACHE_REDIS_PASSWORD = config.CACHE_REDIS_PASSWORD


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())
    register_blueprint(app)
    cache.init_app(app)
    return app


def register_blueprint(app):
    from web import web
    app.register_blueprint(web)


app = create_app()
scheduler = APScheduler();
scheduler.init_app(app=app)
scheduler.start()

scheduler.add_job(func=send_email,max_instances=10, id='send_email', args=(), trigger='interval', seconds=config.SCHEDULER_TIME,
                  replace_existing=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True)
