from flask import Blueprint, request, current_app, render_template, url_for, flash, redirect
from flask_login import current_user, login_required

from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.models import User, Post, Collect
from awesome_flask_webapp.decorators import confirm_required, permission_required
from awesome_flask_webapp.utils import redirect_back

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/user/<int:user_id>')
def index(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_POST_PER_PAGE']
    pagination = Post.query.with_parent(user).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('user/index.html', pagination=pagination, user=user, posts=posts)


@user_bp.route('/<int:user_id>/collections')
def show_collections(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_POST_PER_PAGE']
    pagination = Collect.query.with_parent(user).order_by(Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('user/collections.html', pagination=pagination, user=user, collects=collects)


@user_bp.route('/<int:user_id>/following')
def show_followings(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_USER_PER_PAGE']
    pagination = user.followings.paginate(page, per_page)
    follows = pagination.items
    return render_template('user/followings.html', user=user, pagination=pagination, follows=follows)


@user_bp.route('/<int:user_id>/followers')
def show_followers(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_USER_PER_PAGE']
    pagination = user.followers.paginate(page, per_page)
    follows = pagination.items
    return render_template('user/followers.html', user=user, pagination=pagination, follows=follows)



@user_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
@confirm_required
@permission_required('FOLLOW')
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_following(user):
        flash('Already followed.', 'info')
        return redirect(url_for('user.index', user_id=user_id))

    current_user.follow(user)
    flash('User followed.', 'success')

    return redirect_back()


@user_bp.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_following(user):
        flash('Not follow yet.', 'info')
        return redirect(url_for('user.index', user_id=user_id))

    current_user.unfollow(user)
    flash('User unfollowed.', 'info')
    return redirect_back()
