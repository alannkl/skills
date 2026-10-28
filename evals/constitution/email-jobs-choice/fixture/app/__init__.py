from flask import Flask

from . import cache, routes


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    cache.init_app(app)
    app.register_blueprint(routes.bp)
    return app
