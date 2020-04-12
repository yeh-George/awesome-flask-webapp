# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional, URL, ValidationError
from flask_ckeditor import CKEditorField

from awesome_flask_webapp.models import Category


class TagForm(FlaskForm):
    tag = StringField('Add Tag (use space to separate)', validators=[Optional(), Length(1, 20)])
    submit = SubmitField()


class CategoryForm(FlaskForm):
    category = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('Category already in use.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 100)])
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField()


class LinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 100)])
    url = StringField('Url', validators=[DataRequired(), Length(1, 255), URL()])
    submit = SubmitField()