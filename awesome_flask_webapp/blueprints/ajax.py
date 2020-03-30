from flask import Blueprint, render_template

from awesome_flask_webapp.models import User


ajax_bp = Blueprint('ajax', __name__)


@ajax_bp.route('/profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('main/profile.html', user=user)
