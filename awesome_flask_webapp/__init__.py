# -*- coding: utf-8 -*-
import os
import click

from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
from flask_login import current_user

from awesome_flask_webapp.settings import config
from awesome_flask_webapp.extensions import (
    db, bootstrap, login_manager, mail, ckeditor, moment, csrf, avatars,whooshee, oauth, cache
)
from awesome_flask_webapp.blueprints.main import main_bp
from awesome_flask_webapp.blueprints.auth import auth_bp
from awesome_flask_webapp.blueprints.user import user_bp
from awesome_flask_webapp.blueprints.ajax import ajax_bp
from awesome_flask_webapp.blueprints.admin import admin_bp
from awesome_flask_webapp.blueprints.oauth import oauth_bp
from awesome_flask_webapp.apis.v1 import api_v1
from awesome_flask_webapp.fakes import (
    fake_post, fake_admin, fake_user, fake_categories, fake_tag, fake_comment, fake_follow, fake_collect, fake_link
)
from awesome_flask_webapp.models import User, Post, Comment, Category, Tag, Notification, Collect, Follow, Role, Link


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('awesome_flask_webapp')
    app.wsgi_app = ProxyFix(app.wsgi_app)

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
    avatars.init_app(app)
    whooshee.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': app.config['CACHE_TYPE']})

    register_oauth_and_client(app, oauth)
    csrf.exempt(api_v1)


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ajax_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(api_v1)


def register_errorhandlers(app):
    pass


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Post=Post, Tag=Tag, Role=Role,
                    Follow=Follow, Collect=Collect, Comment=Comment,
                    Notification=Notification, Link=Link, whooshee=whooshee)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        links = Link.query.order_by(Link.name).all()
        categories = Category.query.order_by(Category.name).all()
        if current_user.is_authenticated:
            notification_count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
        else:
            notification_count = 0
        return dict(links=links, categories=categories, notification_count=notification_count)


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

        fake_admin()
        fake_user()
        fake_categories()
        fake_tag()
        fake_post()
        fake_collect()
        fake_comment()
        fake_link()
        click.echo('forge done.')


def register_oauth_and_client(app, oauth):
    oauth.init_app(app)
    # register remote_app (provider)
    oauth.register(
        name='github',
        client_id=os.getenv('GITHUB_CLIENT_ID'),
        client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )