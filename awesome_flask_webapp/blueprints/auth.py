from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user

from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.forms.auth import LoginForm, RegisterForm
from awesome_flask_webapp.models import User


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

        flash("User registered.", "info")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


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

