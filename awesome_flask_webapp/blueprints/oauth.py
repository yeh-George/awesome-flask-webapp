# -*- coding: utf-8 -*-
import os, time

from flask import Blueprint, url_for, render_template, flash, abort, redirect
from flask_login import login_user

from awesome_flask_webapp.extensions import db, oauth
from awesome_flask_webapp.models import User
from awesome_flask_webapp.forms.auth import RegisterSetPasswordForm

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')


provider_endpoints = {
    'github': 'user'
}


def get_profile(provider, token):
    provider_endpoint = provider_endpoints[provider.name]
    resp = provider.get(provider_endpoint)

    data = resp.json()

    if provider.name == 'github':
        username = data.get('login')
        email = data.get('email')
        bio = data.get('bio')

    return username, email, bio


@oauth_bp.route('/login/<provider_name>')
def oauth_login(provider_name):
    provider = oauth.create_client(provider_name)
    callback_uri = url_for('.oauth_authorize', provider_name=provider_name, _external=True)
    return provider.authorize_redirect(callback_uri)


@oauth_bp.route('/callback/<provider_name>')
def oauth_authorize(provider_name):
    time.sleep(10)

    if provider_name not in provider_endpoints.keys():
        abort(404)

    provider = oauth.create_client(provider_name)
    token = provider.authorize_access_token()

    username, email,bio = get_profile(provider, token)

    if username is None:
        flash('Username is empty, please register again.', 'warning')
        return redirect(url_for('auth.register'))

    if User.query.filter_by(username=username).first():
        flash('Username already in user, please register again.', 'warning')
        return redirect(url_for('auth.register'))

    if email is None:
        flash('Email is empty, please register again.', 'warning')
        return redirect(url_for('auth.register'))

    user = User(username=username, email=email, bio=bio)
    db.session.add(user)
    db.session.commit()

    flash('Please set password.', 'warning')
    return redirect(url_for('oauth.set_password', user_id=user.id))


@oauth_bp.route('/set-password/<int:user_id>', methods=['GET', 'POST'])
def set_password(user_id):
    form = RegisterSetPasswordForm()
    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        user.username = form.username.data
        user.set_password(form.password.data)
        user.confirmed = True
        db.session.commit()
        flash('Register success', 'success')
        login_user(user)
        return redirect(url_for('main.index'))

    form.username.data = user.username

    return render_template('auth/register_set_password.html', form=form)

















