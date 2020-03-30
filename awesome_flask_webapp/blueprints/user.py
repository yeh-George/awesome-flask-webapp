from flask import Blueprint

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/<int:user_id>')
def index(user_id):
    pass