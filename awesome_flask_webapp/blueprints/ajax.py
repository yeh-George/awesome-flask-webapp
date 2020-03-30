from flask import Blueprint, render_template, jsonify
from flask_login import current_user

from awesome_flask_webapp.models import User, Post
from awesome_flask_webapp.extensions import db

ajax_bp = Blueprint('ajax', __name__, '/ajax')


@ajax_bp.route('/profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('main/profile.html', user=user)


@ajax_bp.route('/follow/<int:user_id>', methods=['POST'])
def follow(user_id):
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403
    if not current_user.confirmed:
        return jsonify(message='Confirm required.'), 400
    if not current_user.can('COLLECT'):
        return jsonify(message='No permission.'), 403

    user = User.query.get_or_404(user_id)
    if current_user.is_following(user):
        return jsonify(message='Already followed.'), 400

    current_user.follow(user)
    return jsonify(message='Author followed.')


@ajax_bp.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow(user_id):
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403

    user = User.query.get_or_404()
    if not current_user.is_following(user):
        return jsonify(message='Not follow yet.'), 400

    current_user.unfollow(user)
    return jsonify(message='Follow canceled.')



@ajax_bp.route('/followers-count/<int:user_id>')
def followers_count(user_id):
    user = User.query.get_or_404(user_id)
    count = user.followers.count() - 1
    return jsonify(count=count)

