# -*- coding: utf-8 -*-
from flask import Blueprint, request, current_app, render_template, url_for, flash, redirect
from flask_login import current_user, login_required, fresh_login_required, logout_user

from awesome_flask_webapp.settings import Operations
from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.models import User, Post, Collect
from awesome_flask_webapp.decorators import confirm_required, permission_required
from awesome_flask_webapp.utils import redirect_back, generate_token, validate_token
from awesome_flask_webapp.emails import send_change_email_email, send_reset_password_email
from awesome_flask_webapp.forms.user import EditProfileForm, ChangePasswordForm, ChangeEmailForm, \
    NotificationSettingForm, PublicCollectionsSettingForm, DeleteAccountForm
from awesome_flask_webapp.notifications import push_new_follower_notification


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

    if not user.public_collections:
        return render_template('user/collections.html', user=user)

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
    if user.receive_follow_notification:
        push_new_follower_notification(follower=current_user, receiver=user)
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


@user_bp.route('/settings/profile', methods=['GET' ,'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('user.index', user_id=current_user.id))

    form.username.data = current_user.username
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio

    return render_template('user/settings/edit_profile.html', form=form)



@user_bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Password changed.', 'success')
            return redirect(url_for('user.index', user_id=current_user.id))
        else:
            flash('Old Password invalid.', 'warning')

    return render_template('user/settings/change_password.html', form=form)


@user_bp.route('/settings/change-email', methods=['GET', 'POST'])
@fresh_login_required
def change_email():
    form = ChangeEmailForm()

    if form.validate_on_submit():
        token = generate_token(user=current_user, operation=Operations.CHANGE_EMAIL, new_email=form.email.data)
        send_change_email_email(user=current_user, token=token, to=form.email.data)
        flash('Confirm Email sent.', 'info')
        return redirect(url_for('user.index', user_id=current_user.id))

    return render_template('user/settings/change_email.html', form=form)


@user_bp.route('/change-email-confirm/<token>')
@login_required
def change_email_confirm(token):
    if validate_token(user=current_user, token=token, operation=Operations.CHANGE_EMAIL):
        flash('Email updated.', 'success')
        return redirect(url_for('user.index', user_id=current_user.id))
    else:
        flash('Token invalid or expired.', 'warning')
        return redirect(url_for('user.change_email'))


@user_bp.route('/settings/notification', methods=['GET', 'POST'])
@login_required
def notification_setting():
    form = NotificationSettingForm()

    if form.validate_on_submit():
        current_user.receive_collect_notification = form.receive_collect_notification.data
        current_user.receive_comment_notification = form.receive_comment_notification.data
        current_user.receive_follow_notification = form.receive_follow_notification.data
        db.session.commit()
        flash('Notifications setting updated.', 'success')
        return redirect(url_for('user.index', user_id=current_user.id))

    return render_template('user/settings/edit_notification.html', form=form)


@user_bp.route('/settings/privacy', methods=['GET', 'POST'])
@login_required
def privacy_setting():
    form = PublicCollectionsSettingForm()

    if form.validate_on_submit():
        current_user.public_collections = form.public_collections.data
        db.session.commit()
        flash('Privacy settings updated.', 'success')
        return redirect(url_for('.index', user_id=current_user.id))

    form.public_collections.data = current_user.public_collections
    return render_template('user/settings/edit_privacy.html', form=form)


@user_bp.route('/settings/account/delete', methods=['GET', 'POST'])
@fresh_login_required
def delete_account():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        db.session.delete(current_user._get_current_object())
        db.session.commit()
        flash('Goodbye!', 'success')
        logout_user()
        return redirect(url_for('main.index'))

    return render_template('user/settings/delete_account.html', form=form)

