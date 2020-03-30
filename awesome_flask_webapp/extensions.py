from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, AnonymousUserMixin
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_wtf import CSRFProtect
from flask_avatars import Avatars


db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
ckeditor = CKEditor()
moment = Moment()
csrf = CSRFProtect()
avatars = Avatars()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'login'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    from awesome_flask_webapp.models import User
    return User.query.get_or_404(int(user_id))


class Guess(AnonymousUserMixin):

    def can(self, permission_name):
        return False

    @property
    def is_admin(self):
        return False

login_manager.anonymous_user = Guess