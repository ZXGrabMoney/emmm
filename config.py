import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'hard to guess'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.126.com'
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_PORT = '465'
    # app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    # app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    MAIL_USERNAME = 'as_stranger@126.com'
    MAIL_PASSWORD = 'test126'

    @staticmethod
    def init_app(app):
        pass