from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from awesome_flask_webapp.settings import Operations
from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.forms.auth import LoginForm, RegisterForm
from awesome_flask_webapp.models import User
from awesome_flask_webapp.utils import redirect_back, generate_token, validate_token
from awesome_flask_webapp.emails import send_confirm_email


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data.lower()
        password = form.password.data

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = generate_token(user, Operations.CONFIRM)
        send_confirm_email(user, token)
        flash('Confirm Email sent, please check your inbox', 'info')
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    if validate_token(current_user, token, Operations.CONFIRM):
        current_user.confirmed = True
        flash('Account confirmed.', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('auth.resend_confirm_email'))


@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    token = generate_token(current_user, Operations.CONFIRM)
    send_confirm_email(current_user, token)
    flash('Confirm email resent, please check.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user is not None and user.validate_password(password):
            login_user(user, form.remember.data)
            flash('Login success', 'info')
            return redirect(url_for('main.index'))
        flash('Your email or password invalid.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect(url_for('main.index'))

