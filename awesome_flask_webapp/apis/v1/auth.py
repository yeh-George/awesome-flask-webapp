# -*- coding: utf-8 -*-
"""
    generate_token:生成access令牌
    oauth_required:类似于Flask-Login login_required装饰器，通过get_token()获取首部字段中的access令牌，validate_token验证令牌
"""
from functools import wraps

from flask import current_app, url_for, g, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

from awesome_flask_webapp.apis.v1.errors import api_abort
from awesome_flask_webapp.models import User

def  generate_token(user):
    expiration = 3600
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': user.id})
    return token, expiration


def validate_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False

    user = User.query.get(data['id'])
    if user is None:
        return False
    g.current_user = user
    return True


def get_token():
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].splite(None, 1)
        except ValueError:
            token_type = token = None
    else:
        token_type = token = None

    return token_type, token


def oauth_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token_type, token = get_token()
        if request.method != 'OPTIONS':
            if token_type is None or token_type.lower() != 'bearer':
                return api_abort(400, 'The token type must be Bearer.')
            if token is None:
                response = api_abort(401)
                response.headers['WWW-Authenticate'] = 'Bearer'
                return response
            if not validate_token(token):
                response = api_abort(401, 'Token invalid or expired.')
                response.headers['WWW-Authenticate'] = 'Bearer'
                return response
        return func(*args, **kwargs)
    return decorated


