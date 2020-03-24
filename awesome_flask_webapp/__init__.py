import os

from flask import Flask

from awesome_flask_webapp.settings import config
from awesome_flask_webapp.extensions import db, bootstrap
from awesome_flask_webapp.blueprints.main import main_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('awesome_flask_webapp')
    app.config.from_object(config[config_name])

    # 扩展初始化
    register_extensions(app)
    # 注册蓝本
    register_blueprints(app)
    # 注册错误处理函数
    register_errorhandlers(app)
    # 注册模板上下文处理函数
    register_template_context(app)
    # 注册shell上下文处理函数
    register_shell_context(app)
    # 注册自定义shell命令
    register_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)

def register_blueprints(app):
    app.register_blueprint(main_bp)


def register_errorhandlers(app):
    pass


def register_shell_context(app):
    pass


def register_template_context(app):
    pass


def register_commands(app):
    pass


