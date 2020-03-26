from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError

from awesome_flask_webapp.models import User


class ChangeEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254), Email()])
    submit = SubmitField()

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), Length(1, 128), EqualTo('password_confirm')])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField()


class NotificationSettingForm(FlaskForm):
    receive_comment_notification = BooleanField('New Comment')
    receive_followed_notification = BooleanField('New Follower')
    receive_collected_notification = BooleanField('New Collector')
    submit = SubmitField()


class PublicCollectionsSettingForm(FlaskForm):
    public_collections = BooleanField('Public my collections')
    submit = SubmitField()


class DeleteAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_username(self, field):
        if field.data != current_user.username:
            raise ValidationError('Wrong username.')