from flask import Flask
import os


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ['SESSION_KEY']

    from . import main
    app.register_blueprint(main.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
