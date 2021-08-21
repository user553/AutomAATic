from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, RadioField
from wtforms.validators import Length


# reference 3 May https://stackoverflow.com/questions/25297716/how-to-make-radio-field-show-default-value-with-flask-and-wtforms
def create_radio_field(label):
    return RadioField(label, choices=ReviewForm.options, default=3)


class ReviewForm(FlaskForm):
    # reference https://stackoverflow.com/questions/14591202/how-to-make-a-radiofield-in-flask/14591681#14591681
    MAX_COMMENT_LENGTH = 512
    options = [
        (1, 'Strongly disagree'),
        (2, 'Disagree'),
        (3, 'Neither agree nor disagree'),
        (4, 'Agree'),
        (5, 'Strongly Agree')
    ]
    comment = TextAreaField(
        'Additional comments (optional):',
        validators=[Length(max=MAX_COMMENT_LENGTH,
                           message=f'Maximum comment length is 512 characters.')])

    submit = SubmitField('Submit')


class AssessmentReviewForm(ReviewForm):
    # reference https://stackoverflow.com/questions/13404476/inherited-class-variable-modification-in-python/13404537#13404537
    statement1 = create_radio_field(
        'I feel that I had sufficient knowledge to complete this assessment.'
    )
    statement2 = create_radio_field(
        'I found this assessment difficult.'
    )


class AATReviewForm(ReviewForm):
    statement1 = create_radio_field(
        'I find it easy to navigate the AAT to find my tasks that need to be completed.'
    )
    statement2 = create_radio_field(
        'I am pleased overall with the functionality of the AAT.'
    )


class QuestionReviewForm(ReviewForm):
    statement1 = create_radio_field(
        'I found this question difficult to answer.'
    )
    statement2 = create_radio_field(
        'I feel this question is relevant to the topic being assessed.'
    )
