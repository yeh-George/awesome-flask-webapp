from flask import Blueprint


user_bp = Blueprint('user', __name__)

@user_bp.route('/user/<int:user_id>')
def index(user_id):
    pass


@user_bp.route('/user/<int:user_id>/followers')
def show_followers(user_id):
    pass

@user_bp.route('/follow/<int:user_id>', methods=['POST'])
def follow(user_id):
    pass


@user_bp.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow(user_id):
    pass