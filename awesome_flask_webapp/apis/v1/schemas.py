# -*- coding: utf-8 -*-
"""
    资源序列化
"""
from flask import url_for


def user_schema(user):
    return {
        'id': user.id,
        'self': url_for('.user', user_id=user.id,  _external=True),
        'kind': 'User',
        'username': user.username
    }


def post_schema(post):
    return {
        'id': post.id,
        'self': url_for('.post', post_id=post.id, _external=True),
        'kind': 'Post',
        'title': post.title,
        'body': post.body,
        'author': {
            'id': post.author.id,
            'homepage_url': url_for('.user', user_id=post.author.id, _external=True),
            'username': post.author.username,
            'kind': 'User',
        },
        'comments': [comment_schema(comment) for comment in post.comments]
    }


def comment_schema(comment):
    return {
        'id': comment.id,
        'body': comment.body,
        'author': {
            'id': comment.author.id,
            'homepage_url': url_for('.user', user_id=comment.author.id, _external=True),
            'username': comment.author.username,
            'kind': 'User',
        },
        'replied_id': comment.replied_id
    }


def posts_schema(posts, current, prev, next, pagination):
    return {
        'self': current,
        'kind': 'PostCollection',
        'posts': [post_schema(post) for post in posts],
        'prev': prev,
        'last': url_for('.posts', page=pagination.pages, _external=True),
        'first': url_for('.posts', page=1, _external=True),
        'next': next,
        'count': pagination.total
    }