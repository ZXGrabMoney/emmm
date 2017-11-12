from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
from .models import HttpAuth

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

dbdir=os.path.join(basedir,'data.db')
print(dbdir)
httpauth=HttpAuth()

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
#db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    #bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
 #   db.init_app(app)

    app.jinja_env.variable_start_string="{{ "
    app.jinja_env.variable_end_string=" }}"

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .pair import pair as pair_blueprint
    app.register_blueprint(pair_blueprint)

    return app