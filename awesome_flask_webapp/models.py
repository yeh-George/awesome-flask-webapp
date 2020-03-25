from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from awesome_flask_webapp.extensions import db


permissions_roles = db.Table(
    'permissions_roles',
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)

    roles = db.relationship('Role', secondary=permissions_roles, back_populates='permissions')


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)

    permissions = db.relationship('Permission', secondary=permissions_roles, back_populates='roles')
    users = db.relationship('User', back_populates='role')

    @staticmethod
    def init_role():
        role_permission_map = {
            'Locked': ['FOLLOW', 'COLLECT'],
            'User': ['FOLLOW', 'COLLECT', 'COMMENT', 'POST'],
            'Moderator': ['FOLLOW', 'COLLECT', 'COMMENT', 'POST', 'MODERATE'],
            'Administrator': ['FOLLOW', 'COLLECT', 'COMMENT', 'POST', 'MODERATE', 'ADMINISTER']
        }

        for role_name in role_permission_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in role_permission_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='followings', lazy='joined')
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followers', lazy='joined' )


class Collect(db.Model):
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    collected_id = db.Column(db.Integer, db.ForeignKey('post.id', primary_key=True))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    collector = db.relationship('User', back_populates='collections', lazy='joined') # user
    collected = db.relationship('Post', back_populates='collectors', lazy='joined') # post


class User(db.Model, UserMixin):
    # account info
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    # user info
    name = db.Column(db.String(30))
    bio = db.Column(db.String(255))
    location = db.Column(db.String(50))
    memeber_since = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed =db.Column(db.Boolean, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    role = db.relationship('Role', back_populates='users')
    posts = db.relationship('Post', back_populates='author')
    comments = db.relationship('Comment', back_populates='author')
    collections = db.relationship('Collect', back_populates='collector')
    followings = db.relationship('Follow', foreign_keys=[Follow.follower_id], back_populates='follower', lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed', lazy='dynamic')
    notifications = db.relationship('Notification', back_populates='receiver')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


tags_posts = db.Table(
    'tags_posts',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True, unique=True)

    posts = db.relationship('Post', secondary=tags_posts, back_populates='tags')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    can_comment = db.Column(db.Boolean, default=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    author = db.relationship('User', back_populates='posts')
    tags = db.relationship('Tag', secondary=tags_posts, back_populates='posts')
    comments = db.relationship('Comment', back_populates='post')
    collector = db.relationship('Collect', back_populates='collected')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # 评论的作者
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='comments')
    # 评论的文章
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='post')
    # 评论下的回复
    replies = db.relationship('Comment', back_populates='replied')
    # 回复的评论
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replied = db.relationship('Comment', back_populates='replies', remote_id=[id])


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    receiver = db.relationship('User', back_populates='notifications')


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(255))
