from flask import Blueprint, render_template, url_for

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/about')
def about():
    return '<h1>about</h1>'