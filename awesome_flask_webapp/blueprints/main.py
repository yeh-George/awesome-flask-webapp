from flask import Blueprint, render_template, url_for, request, flash, current_app, abort, redirect

from flask_login import login_required, current_user

from awesome_flask_webapp.utils import redirect_back
from awesome_flask_webapp.models import Notification, Post, Comment
from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.forms.main import CommentForm


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('main/index.html', pagination=pagination, posts=posts)


@main_bp.route('/about')
def about():
    return render_template('main/about.html')


@main_bp.route('/notifications')
@login_required
def show_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_NOTIFICATION_PER_PAGE']
    notifications = Notification.query.with_parent(current_user)
    filter_rule = request.args.get('filter')
    if filter_rule == 'unread':
        notifications = notifications.filter_by(is_read=False)

    pagination = notifications.order_by(Notification.timestamp.desc()).paginate(page, per_page)
    notifications = pagination.items
    return render_template('main/notifications.html', pagination=pagination, notifications=notifications)


@main_bp.route('/notification/read/<int:notification_id>')
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if current_user != notification.receiver:
        abort(403)

    notification.is_read = True
    db.session.commit()
    flash('Notification read.', 'success')
    return redirect(url_for('.show_notifications'))


@main_bp.route('/notification/read/all')
@login_required
def read_all_notifications():
    for notification in current_user.notifications:
        notification.is_read = True
    db.session.commit()
    flash('All notifications read.', 'success')
    return redirect(url_for('.show_notifications'))


@main_bp.route('/post/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items

    comment_form = CommentForm()

    return render_template('main/post.html', pagination=pagination, post=post, comments=comments,
                           comment_form=comment_form)



@main_bp.route('/collect/<int:post_id>', methods=['POST'])
def collect(post_id):
    pass


@main_bp.route('/uncollect/<int:post_id>', methods=['POST'])
def uncollect(post_id):
    pass


@main_bp.route('/post/<int:post_id>/collectors')
def show_collectors(post_id):
    pass


@main_bp.route('/category/<int:category_id>')
def show_category(category_id):
    pass


@main_bp.route('/tag/<int:tag_id>')
def show_tag(tag_id):
    pass

