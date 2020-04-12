# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, redirect, request, current_app, flash
from flask_login import login_required


from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.models import Role, User, Post, Category, Comment, Tag, Link
from awesome_flask_webapp.decorators import admin_required, permission_required
from awesome_flask_webapp.utils import redirect_back
from awesome_flask_webapp.forms.admin import LinkForm, EditProfileAdminForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
def index():
    user_count = User.query.count()
    post_count = Post.query.count()
    category_count = Category.query.count()
    tag_count = Tag.query.count()
    comment_count = Comment.query.count()
    link_count = Link.query.count()

    return render_template('admin/index.html', user_count=user_count, post_count=post_count,
                           category_count=category_count, tag_count=tag_count,
                           comment_count=comment_count, link_count=link_count)


@admin_bp.route('/manage/user')
@login_required
@permission_required('MODERATE')
def manage_user():
    filter_rule = request.args.get('filter', 'all') # all,
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_MANAGE_PER_PAGE']

    administrator = Role.query.filter_by(name='Administrator').first()
    moderator = Role.query.filter_by(name='Moderator').first()

    if filter_rule == 'locked':
        filtered_users = User.query.filter_by(locked=True)
    elif filter_rule == 'blocked':
        filtered_users = User.query.filter_by(blocked=True)
    elif filter_rule == 'administrator':
        filtered_users = User.query.filter_by(role=administrator)
    elif filter_rule == 'moderator':
        filtered_users = User.query.filter_by(role=moderator)
    else:
        filtered_users = User.query

    pagination = filtered_users.order_by(User.member_since.desc()).paginate(page, per_page)
    users = pagination.items
    for user in users:
        print(user.username, user.avatar_s)

    return render_template('admin/manage_user.html', pagination=pagination, users=users)



@admin_bp.route('/manage/post')
@login_required
@permission_required('MODERATE')
def manage_post():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_MANAGE_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination, posts=posts)


@admin_bp.route('/manage/category')
def manage_category():
    pass


@admin_bp.route('/manage/tag')
def manage_tag():
    pass


@admin_bp.route('/manage/comment')
@login_required
@permission_required('MODERATE')
def manage_comment():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_MANAGE_PER_PAGE']
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items

    for comment in comments:
        print(comment.id)
        print(comment.post.id)
        print(comment.author.id)
        print()
    return render_template('admin/manage_comment.html', pagination=pagination, comments=comments)



@admin_bp.route('/manage/link')
@login_required
@permission_required('MODERATE')
def manage_link():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['AWESOME_MANAGE_PER_PAGE']
    pagination = Link.query.order_by(Link.name).paginate(page, per_page)
    links = pagination.items

    return render_template('admin/manage_link.html', pagination=pagination, links=links)



@admin_bp.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    user = User.query.get_or_404(user_id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():
        user.name = form.name.data
        role = Role.query.get(form.role.data)
        if role.name == 'Locked':
            user.lock()

        user.role = role
        user.bio = form.bio.data
        user.confirmed = form.confirmed.data
        user.active = form.active.data
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect_back()

    form.name.data = user.name
    form.role.data = user.role_id
    form.bio.data = user.bio
    form.username.data = user.username
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.blocked.data = user.blocked
    return render_template('admin/edit_profile_admin.html', form=form, user=user)


@admin_bp.route('/block/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role.name in ['Administrator', 'Moderator']:
        flash('Permission denied.', 'warning')
    else:
        user.block()
        flash('Account blocked.', 'info')
    return redirect_back()


@admin_bp.route('/unblock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unblock()
    flash('Block canceled.', 'info')
    return redirect_back()


@admin_bp.route('/lock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def lock_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role.name in ['Administrator', 'Moderator']:
        flash('Permission denied.', 'warning')
    else:
        user.lock()
        flash('Account locked.', 'info')
    return redirect_back()


@admin_bp.route('/unlock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def unlock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unlock()
    flash('Lock canceled.', 'info')
    return redirect_back()


@admin_bp.route('/link/new', methods=['GET', 'POST'])
@login_required
@permission_required('MODERATE')
def new_link():
    form = LinkForm()

    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        link = Link(name=name, url=url)
        db.session.add(link)
        db.session.commit()
        flash('Link created.', 'info')
        return redirect(url_for('admin.manage_link'))

    return render_template('admin/new_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('MODERATE')
def edit_link(link_id):
    form = LinkForm()
    link = Link.query.get_or_404(link_id)

    if form.validate_on_submit():
        link.name = form.name.data
        link.url = form.url.data
        db.session.commit()
        flash('Link updated.', 'info')
        return redirect(url_for('admin.manage_link'))

    form.name.data = link.name
    form.url.data = link.url
    return render_template('admin/edit_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/delete', methods=['POST'])
@login_required
@permission_required('MODERATE')
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted.', 'info')
    return redirect_back()


