from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_wtf import CSRFProtect

db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
ckeditor = CKEditor()
moment = Moment()
csrf = CSRFProtect()

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from awesome_flask_webapp.models import User
    return User.query.get_or_404(int(user_id))