from flask import Blueprint, render_template, jsonify
from flask_login import current_user

from awesome_flask_webapp.models import User, Post, Notification
from awesome_flask_webapp.notifications import push_new_follower_notification

ajax_bp = Blueprint('ajax', __name__, url_prefix='/ajax')


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
    if user.receive_follow_notification:
        push_new_follower_notification(follower=current_user, receiver=user)
    return jsonify(message='Author followed.')


@ajax_bp.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow(user_id):
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403

    user = User.query.get_or_404(user_id)
    if not current_user.is_following(user):
        return jsonify(message='Not follow yet.'), 400

    current_user.unfollow(user)
    return jsonify(message='Follow canceled.')



@ajax_bp.route('/followers-count/<int:user_id>')
def followers_count(user_id):
    user = User.query.get_or_404(user_id)
    count = user.followers.count() - 1
    return jsonify(count=count)


@ajax_bp.route('/notification-count')
def notification_count():
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403

    count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
    return jsonify(count=count)