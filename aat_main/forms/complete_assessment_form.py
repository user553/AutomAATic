from flask_wtf import FlaskForm
from wtforms import SubmitField


class complete_assessment_form(FlaskForm):
    submit = SubmitField()
