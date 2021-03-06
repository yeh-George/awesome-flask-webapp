# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, request, flash, current_app, abort, redirect, send_from_directory

from flask_login import login_required, current_user

from awesome_flask_webapp.utils import redirect_back
from awesome_flask_webapp.decorators import confirm_required, permission_required
from awesome_flask_webapp.models import Notification, Post, Comment, Category, Tag, Collect, Follow, User
from awesome_flask_webapp.extensions import db, cache
from awesome_flask_webapp.forms.main import CommentForm, PostForm
from awesome_flask_webapp.notifications import push_new_comment_notification, push_new_collector_notification


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('main/index.html', pagination=pagination, posts=posts)


@main_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
@confirm_required
@permission_required('POST')
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        category = Category.query.get_or_404(form.category.data)
        body = form.body.data

        post = Post(title=title, body=body, category=category, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created', 'success')
        return redirect(url_for('user.index', user_id=current_user.id))

    return render_template('main/new_post.html', form=form)


@main_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@confirm_required
@permission_required('POST')
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = Category.query.get(form.category.data)
        post.body = form.body.data

        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('user.index', user_id=current_user.id))

    form.title.data = post.title
    form.category.data = post.category.id
    form.body.data = post.body

    return render_template('main/edit_post.html', form=form)


@main_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user != post.author and not current_user.can('MODERATE'):
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()


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


@main_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)

    if post.can_comment:
        post.can_comment = False
        flash('Post comment disabled.', 'info')
    else:
        post.can_comment = True
        flash('Post comment enabled.', 'info')
    db.session.commit()
    return redirect(url_for('main.show_post', post_id=post_id))


@main_bp.route('/post/<int:post_id>/comment/new', methods=["POST"])
@login_required
@permission_required('COMMENT')
def new_comment(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    form = CommentForm()

    if form.validate_on_submit():
        body = form.body.data
        author = current_user._get_current_object()
        comment = Comment(body=body, author=author, post=post)

        replied_id = request.args.get('reply')
        if replied_id:
            comment.replied = Comment.query.get_or_404(replied_id)
            if comment.replied.author.receive_comment_notification:
                push_new_comment_notification(post_id=post_id, receiver=comment.replied.author)

        db.session.add(comment)
        db.session.commit()
        flash("Comment published.", 'success')

        if current_user is not post.author and post.author.receive_comment_notification:
            push_new_comment_notification(post_id=current_user.id, receiver=post.author, page=page)

        return redirect(url_for('.show_post', post_id=post_id, page=page))

    flash('Invalid comment.', 'warning')
    return redirect(url_for('main.show_post', post_id=post.id, page=page))


@main_bp.route('/reply/comment/<int:comment_id>')
@login_required
@permission_required('COMMENT')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('main.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author.name)
                    + '#comment-form')


@main_bp.route('/delete/comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author and current_user != comment.post.author and not current_user.can('MODERATE'):
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    if request.args.get('next'):
        return redirect_back()
    return redirect(url_for('main.show_post', post_id=comment.post_id) + '#comments')


@main_bp.route('/collect/<int:post_id>', methods=['POST'])
@login_required
@confirm_required
@permission_required('COLLECT')
def collect(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_collecting(post):
        flash('Already collecting', 'info')
        return redirect(url_for('main.show_post', post_id=post_id))

    current_user.collect(post)
    flash('Post collected.', 'success')
    if current_user != post.author and post.author.receive_collect_notification:
        push_new_collector_notification(collector=current_user, post_id=post.id, receiver=post.author)
    return redirect(url_for('main.show_post', post_id=post_id))


@main_bp.route('/uncollect/<int:post_id>', methods=['POST'])
@login_required
def uncollect(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_collecting(post):
        flash('Not collecting.', 'info')
        return redirect(url_for('main.show_post', post_id=post.id))

    current_user.uncollect(post)
    flash('Post uncollected.', 'success')
    return redirect(url_for('main.show_post', post_id=post_id))


@main_bp.route('/post/<int:post_id>/collectors')
@cache.cached(timeout=60)
def show_collectors(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_USER_PER_PAGE']
    pagination = Collect.query.with_parent(post).order_by(Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('main/collectors.html', pagination=pagination, collects=collects, post=post)


@main_bp.route('/category/<int:category_id>')
@cache.cached(timeout=60)
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('main/category.html', pagination=pagination, posts=posts, category=category)


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


@main_bp.route('/notification/read/<int:notification_id>', methods=['POST'])
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if current_user != notification.receiver:
        abort(403)

    notification.is_read = True
    db.session.commit()
    flash('Notification read.', 'success')
    return redirect(url_for('.show_notifications'))


@main_bp.route('/notification/read/all', methods=['POST'])
@login_required
def read_all_notifications():
    for notification in current_user.notifications:
        notification.is_read = True
    db.session.commit()
    flash('All notifications read.', 'success')
    return redirect(url_for('.show_notifications'))


@main_bp.route('/avatar/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


@main_bp.route('/about')
@cache.cached(timeout=3600 * 24)
def about():
    return render_template('main/about.html')


@main_bp.route('/search')
def search():
    q = request.args.get('q', '')
    if q == '':
        flash('Please enter something.', 'warning')
        return redirect_back()

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_SEARCH_PER_PAGE']
    category = request.args.get('category', 'user')

    if category == 'user':
        result_count = User.query.whooshee_search(q).count()
        pagination = User.query.whooshee_search(q).paginate(page, per_page)
    elif category == 'tag':
        result_count = Tag.query.whooshee_search(q).count()
        pagination = Tag.query.whooshee_search(q).paginate(page, per_page)
    else:
        result_count = Post.query.whooshee_search(q).count()
        pagination = Post.query.whooshee_search(q).paginate(page, per_page)

    results = pagination.items

    return render_template('main/search.html',q=q, pagination=pagination, category=category, results=results,
                           result_count=result_count)