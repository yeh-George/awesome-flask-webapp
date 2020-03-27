from faker import Faker

from awesome_flask_webapp.extensions import db
from awesome_flask_webapp.models import Post


fake = Faker()


def fake_post():
    for i in range(50):
        post = Post(
            title = fake.sentence(),
            body = fake.text(800),
            timestamp = fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()