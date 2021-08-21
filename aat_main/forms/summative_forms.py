from flask_wtf import FlaskForm

from wtforms import SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, ValidationError, Length


class assessment_form(FlaskForm):
    def validate_module(form, module):
        if module.data == "Please Choose a Module":
            raise ValidationError("Please Choose a Module!")

    def validate_title(form, title):
        if len(title.data) < 5:
            raise ValidationError("Title must be between 5 - 64 characters")

    title = TextAreaField('Assessment Title', validators=[DataRequired(), Length(min=5, max=64)])
    # Course will be changed to only show courses that each lecturer is on. 
    module = SelectField(choices=[], default="Please choose a module")
    description = TextAreaField('Assessment Description', validators=[DataRequired(), Length(min=0, max=512)])
    start_date = DateField("Start Date", format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField("Start Time", validators=[DataRequired()])
    end_date = DateField("End Date", format='%Y-%m-%d', validators=[DataRequired()])
    end_time = TimeField("End Time", validators=[DataRequired()])
    timelimit = IntegerField("Minutes")
    submit = SubmitField()


class summative_edit_form(FlaskForm):
    submit = SubmitField()
