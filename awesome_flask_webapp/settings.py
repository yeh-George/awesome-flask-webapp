import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Operations(object):
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class BaseConfig(object):
    AWESOME_ADMIN_EMAIL = os.getenv('AWESOME_ADMIN_EMAIL', 'yechenjia20@outlook.com')

    SECRET_KEY = os.getenv('SECRET_KEY', 'secret key')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BOOTSTRAP_SERVE_LOCAL = True
    # mail config
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Ye Chenjia', MAIL_USERNAME)


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///' + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
