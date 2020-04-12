# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Operations(object):
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class BaseConfig(object):
    AWESOME_ADMIN_EMAIL = os.getenv('AWESOME_ADMIN_EMAIL', 'yechenjia20@outlook.com')
    AWESOME_USER_PER_PAGE = 25
    AWESOME_POST_PER_PAGE = 15
    AWESOME_COMMENT_PER_PAGE = 15
    AWESOME_NOTIFICATION_PER_PAGE = 20
    AWESOME_MANAGE_PER_PAGE = 10
    AWESOME_SEARCH_PER_PAGE = 10

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

    # avatar
    AVATARS_SAVE_PATH = os.path.join(basedir, 'avatars')
    AVATARS_SIZE_TUPLE = (30, 100, 200)

    # Whooshee
    WHOOSHEE_MIN_STRING_LEN = 1
    # cache


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.db')

    CACHE_TYPE = 'null'
    CACHE_NO_NULL_WARNING = True


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_TIMEOUT = 600
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///' + os.path.join(basedir, 'data.db'))
    #cache redis
    CACHE_TYPE = 'redis'

    CACHE_DEFAULT_TIMEOUT = 60
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_DB = '0'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
