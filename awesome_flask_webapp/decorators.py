# -*- coding: utf-8 -*-
from functools import wraps

from flask import Markup, url_for, redirect, abort, flash
from flask_login import current_user


def confirm_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if not current_user.confirmed:
            message = Markup(
                'Please confirm your account first.'
                ' Not receive the confirm email? '
                ' <a href="%s" > Resend Confirm Email.</a> ' %
                    url_for('auth.resend_confirm_email')
            )
            flash(message, 'warning')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorated_func


def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            if not current_user.can(permission_name):
                abort(403)
            return func(*args, **kwargs)
        return decorated_func
    return decorator


def admin_required(func):
    return permission_required('ADMINISTER')(func)