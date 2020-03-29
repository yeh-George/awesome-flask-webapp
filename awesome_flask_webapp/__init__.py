import os
import click

from flask import Flask

from awesome_flask_webapp.settings import config
from awesome_flask_webapp.extensions import db, bootstrap, login_manager, mail, ckeditor, moment, csrf
from awesome_flask_webapp.blueprints.main import main_bp
from awesome_flask_webapp.blueprints.auth import auth_bp
from awesome_flask_webapp.fakes import (
    fake_post, fake_admin, fake_user, fake_categories, fake_tag, fake_comment, fake_follow, fake_collect
)
from awesome_flask_webapp.models import User, Post, Comment, Category, Tag, Notification, Collect, Follow, Role


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
    login_manager.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)


def register_errorhandlers(app):
    pass


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Post=Post, Tag=Tag,
                    Follow=Follow, Collect=Collect, Comment=Comment,
                    Notification=Notification)


def register_template_context(app):
    pass


def register_commands(app):
    @app.cli.command()
    def init_db():
        db.drop_all()
        db.create_all()
        Role.init_role()
        click.echo('database initialized.')

    @app.cli.command()
    def forge():
        db.drop_all()
        db.create_all()
        Role.init_role()

        print(1)
        fake_admin()
        print(1)
        fake_user()
        print(1)
        fake_categories()
        fake_tag()
        fake_post()
        print(1)
        fake_collect()
        print(1)
        fake_comment()
        click.echo('forge done.')
