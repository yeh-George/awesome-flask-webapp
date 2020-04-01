from flask import url_for

from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.models import Notification


def push_new_follower_notification(follower, receiver):
    message = 'User <a href="%s"> %s </a> follows you.' % \
              (url_for('user.index', user_id=follower.id), follower.username)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_new_comment_notification(post_id, receiver, page=1):
    message = 'This <a href="%s" > post </a> has new comment/reply.' % \
              url_for('main.show_post', post_id=post_id, page=page)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_new_collector_notification(collector, post_id, receiver):
    message = 'This <a href="%s" > post </a> has been collected by <a href="%s" > %s </a>.' % \
          (url_for('main.show_post', post_id=post_id), url_for('user.index', user_id=collector.id), collector.username)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()