from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class question_form(FlaskForm):
    name = TextAreaField('Question Name', validators=[DataRequired()])
    course = TextAreaField('Course', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')
