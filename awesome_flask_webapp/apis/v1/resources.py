# -*- coding: utf-8 -*-
"""
    资源端点设计：
    资源       URL                方法
    单个用户    /user/<user_id>     GET
    单篇文章    /posts/<post_id>    GET
    所有文章集合 /posts             GET
    当前用户    /user               GET
    当前用户单篇文章 /user/posts/<post_id> GET, PUT, PATH, DELETE
    当前用户所有文章集合 /user/posts    GET, POST
"""
from flask import jsonify, request, current_app, url_for, g
from flask.views import MethodView

from awesome_flask_webapp.apis.v1.auth import generate_token, oauth_required
from awesome_flask_webapp.models import User, Post
from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.apis.v1.errors import api_v1, ValidationError, api_abort
from awesome_flask_webapp.apis.v1.schemas import user_schema, post_schema, posts_schema


class IndexAPI(MethodView):

    def get(self):
        return jsonify({
            "api_version": "1.0",
            "api_base_url": "http://example.com/api/v1",
            "user_url": "http://example.com/api/v1/user/{user_id}",
            "posts_url": "http://example.com/api/v1/posts{?page,per_page}",
            "post_url": "http://example.com/api/v1/posts/{post_id}",
            "current_user_url": "http://example.com/api/v1/user",
            "current_user_posts_url": "http://example.com/api/v1/user/posts{?page,per_page}",
            "current_user_post_url": "http://example.com/api/v1/user/post/{post_id}",
        })


class UserAPI(MethodView):

    def get(self, user_id):
        """Get user."""
        user = User.query.get_or_404(user_id)
        return jsonify(user_schema(user))


class PostAPI(MethodView):

    def get(self, post_id):
        """Get post."""
        post = Post.query.get_or_404(post_id)
        return jsonify(post_schema(post))


class PostsAPI(MethodView):

    def get(self):
        """Get all posts."""
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['AWESOME_POST_PER_PAGE']
        pagination = Post.query.paginate(page, per_page)
        posts = pagination.items
        current = url_for('.posts', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.posts', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.posts', page=page + 1, _external=True)
        return jsonify(posts_schema(posts, current, prev, next, pagination))


class CurrentUserAPI(MethodView):
    decorators = [oauth_required]

    def get(self):
        """Get current user."""
        return jsonify(user_schema(g.current_user))


class CurrentUserPostsAPI(MethodView):
    decorators = [oauth_required]

    def get(self):
        """Get current user's all posts."""
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['AWESOME_POST_PER_PAGE']
        pagination = Post.query.with_parent(g.current_user).paginate(page, per_page)
        posts = pagination.items
        current = url_for('.current_user_posts', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.current_user_posts', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.current_user_posts', page=page + 1, _external=True)
        return jsonify(posts_schema(posts, current, prev, next, pagination))

    def post(self):
        """Create new post."""
        data = request.get_json()
        title = data.get('title')
        body = data.get('body')

        if title is None or str(body).strip() == '':
            raise ValidationError('The post body was empty or invalid.')
        if body is None or str(body).strip() == '':
            raise ValidationError('The post body was empty or invalid.')

        post = Post(title=title, body=body, author=g.current_user)
        db.session.add(post)
        db.session.commit()

        # POST: 返回（指向数据新地址的表现层 + 首部字段Location为指向资源的URL + 201）
        response = jsonify(post_schema(post))
        response.headers['Location'] = url_for('.post', post_id=post.id, _external=True)
        return response, 201


class CurrentUserPostAPI(MethodView):
    decorators = [oauth_required]

    def get(self, post_id):
        """Get current user post."""
        post = Post.query.get_or_404(post_id)
        if g.current_user != post.author:
            return api_abort(403)
        return jsonify(post_schema(post))

    def put(self, post_id):
        """Edit item."""
        post = Post.query.get_or_404(post_id)
        if g.current_user != post.author:
            return api_abort(403)

        data = request.get_json()
        title = data.get('title')
        body = data.get('body')

        if title is None or str(body).strip() == '':
            raise ValidationError('The post body was empty or invalid.')
        if body is None or str(body).strip() == '':
            raise ValidationError('The post body was empty or invalid.')

        post.title = title
        post.body = body
        db.session.commit()
        return '', 204

    def patch(self, post_id):
        """Toggle post can_comment."""
        post = Post.query.get_or_404(post_id)
        if g.current_user != post.author:
            return api_abort(403)
        post.done = not post.can_comment
        db.session.commit()
        return '', 204

    def delete(self, post_id):
        """Delete post."""
        post = Post.query.get_or_404(post_id)
        if g.current_user != post.author:
            return api_abort(403)
        db.session.delete(post)
        db.session.commit()
        return '', 204


class AuthTokenAPI(MethodView):

    def post(self):
        # Resource Owner Password Credentials
        # grant_type, username, password, scope
        grant_type = request.form.get('grant_type')
        username = request.form.get('username')
        password = request.form.get('passowrd')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(code=400, message='grant type must be password.')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.validate_password(password):
            return api_abort(400, message='Username or password invalid.')

        token, expiration = generate_token(user)

        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'

        return response



api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/user/<int:user_id>', view_func=UserAPI.as_view('user'), methods=['GET'])
api_v1.add_url_rule('/posts/<int:post_id>', view_func=PostAPI.as_view('post'), methods=['GET'])
api_v1.add_url_rule('/posts', view_func=PostsAPI.as_view('posts'), methods=['GET'])
api_v1.add_url_rule('/user', view_func=CurrentUserAPI.as_view('current_user', methods=['GET']))
api_v1.add_url_rule('/user/posts/<int:post_id>', view_func=CurrentUserPostAPI.as_view('current_user_post'),
                    methods=['GET', 'PUT', 'PATCH', 'DELETE'])
api_v1.add_url_rule('/user/posts', view_func=CurrentUserPostsAPI.as_view('current_user_posts'), methods=['GET', 'POST'])

api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])