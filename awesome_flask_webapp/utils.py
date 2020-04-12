# -*- coding: utf-8 -*-
from urllib.parse import urlparse, urljoin

from flask import current_app, request, redirect, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.models import User
from awesome_flask_webapp.settings import Operations

#检测url是不是安全
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and test_url.netloc == ref_url.netloc

#返回上一页next / referrer
def redirect_back(default='main.index', **kwargs):
    for target in (request.args.get('next'), request.referrer):
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

# 生成邮件验证的令牌
def generate_token(user, operation, expires_in=None, **kwargs):
    s = Serializer(secret_key=current_app.config['SECRET_KEY'], expires_in=expires_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


# 验证邮件验证的令牌
def validate_token(user, operation, token):
    s = Serializer(secret_key=current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first():
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True