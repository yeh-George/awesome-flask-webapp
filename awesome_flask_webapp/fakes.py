# -*- coding: utf-8 -*-
import os
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.models import User, Post, Tag, Comment, Notification, Category, Link

fake = Faker()


def fake_admin():
    admin = User(name='Grey Li',
                 username='greyli',
                 email='admin@helloflask.com',
                 bio=fake.sentence(),
                 confirmed=True)
    admin.set_password('helloflask')
    notification = Notification(message='Hello, welcome to Albumy.', receiver=admin)
    db.session.add(notification)
    db.session.add(admin)
    db.session.commit()


def fake_user(count=10):
    for i in range(count):
        user = User(name=fake.name(),
                    confirmed=True,
                    username=fake.user_name(),
                    bio=fake.sentence(),
                    location=fake.city(),
                    member_since=fake.date_this_decade(),
                    email=fake.email())
        user.set_password('123456')
        notification = Notification(message='Hello, welcome to Albumy.', receiver=user)
        db.session.add(notification)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_follow(count=30):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.follow(User.query.get(random.randint(1, User.query.count())))
    db.session.commit()


def fake_tag(count=20):
    for i in range(count):
        tag = Tag(name=fake.word())
        db.session.add(tag)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_post(count=30):
    for i in range(count):
        print(i)

        post = Post(
            title=fake.sentence(),
            body=fake.text(),
            author=User.query.get(random.randint(1, User.query.count())),
            category=Category.query.get(random.randint(1, User.query.count())),
            timestamp=fake.date_time_this_year()
        )

        # tags
        for j in range(random.randint(1, 5)):
            tag = Tag.query.get(random.randint(1, Tag.query.count()))
            if tag not in post.tags:
                post.tags.append(tag)

        db.session.add(post)
    db.session.commit()


def fake_collect(count=50):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.collect(Post.query.get(random.randint(1, Post.query.count())))
    db.session.commit()


def fake_comment(count=100):
    for i in range(count):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()


def fake_link():
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    linkedin = Link(name='LinkedIn', url='#')
    google = Link(name='Google+', url='#')
    db.session.add_all([twitter, facebook, linkedin, google])
    db.session.commit()