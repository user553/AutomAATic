from flask import Blueprint, render_template
from flask_login import login_required, current_user

from aat_main.models.assessment_models import Assessment
from aat_main.models.question_models import Question
from aat_main.models.satisfaction_review_models import AATReview
from aat_main.utils.authorization_helper import check_if_authorized
from aat_main.utils.serialization_helper import SerializationHelper

satisfaction_result_bp = Blueprint('satisfaction_result_bp', __name__, url_prefix='/review/results',
                                   template_folder='../views/satisfaction_results')

responses = {
    '1': 'Strongly disagree',
    '2': 'Disagree',
    '3': 'Neither agree nor disagree',
    '4': 'Agree',
    '5': 'Strongly agree'
}


@satisfaction_result_bp.before_request
@login_required
def before_request():
    authorized_role = 'lecturer'
    check_if_authorized(authorized_role)


@satisfaction_result_bp.route('/')
def home():
    # links = {
    #     'automAATiq': 'assessment_review_results',
    #     'Assessments': ''
    # }
    assessments = current_user.get_available_assessments_lecturer()
    return render_template('home.html', assessments=assessments)


@satisfaction_result_bp.route('/assessment/<id>')
def assessment_review_results(id):
    assessment = Assessment.get_assessment_by_id(id)
    reviews = assessment.get_reviews()
    if not reviews:
        return render_template('no-reviews-assessment.html', assessment=assessment)

    statement_response_counts = SerializationHelper.decode(reviews, responses)

    # TODO maybe add mentimeter-style visualization (including mean?)
    comments = [review.comment for review in reviews if review.comment]

    title = f'Results of Reviews for {assessment.title}'
    return render_template('satisfaction_results/review-results.html', assessment=assessment,
                           results=statement_response_counts, comments=comments,
                           responses=responses, page_title=title)


@satisfaction_result_bp.route('/aat')
def aat_review_results():
    # reference https://stackoverflow.com/questions/455612/limiting-floats-to-two-decimal-points/455634#455634. 22 March
    # means = ['{:.2f}'.format(mean(answers)) for answers in statement_answers]

    reviews = AATReview.get_all_reviews()
    # TODO handle case where there are no reviews

    statement_response_counts = SerializationHelper.decode(reviews, responses)

    # TODO maybe add mentimeter-style visualization (including mean?)

    comments = [review.comment for review in reviews if review.comment]

    title = 'Result of satisfaction reviews for automAATiq'

    return render_template('satisfaction_results/review-results.html',
                           results=statement_response_counts,
                           comments=comments, responses=responses,
                           page_title=title)


@satisfaction_result_bp.route('/question/<id>')
def question_review_result(id):
    question = Question.get_question_by_id(id)
    reviews = question.get_reviews()
    if not reviews:
        return render_template('no-reviews-question.html', question=question)

    # TODO handle case where there are no reviews

    statement_response_counts = SerializationHelper.decode(reviews, responses)

    # TODO maybe add mentimeter-style visualization (including mean?)
    comments = [review.comment for review in reviews if review.comment]

    title = f'Results of reviews for {question.name}'
    return render_template('satisfaction_results/review-results.html', question=question,
                           results=statement_response_counts, comments=comments,
                           responses=responses, page_title=title)
