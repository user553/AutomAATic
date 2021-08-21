import json
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user

from aat_main.forms.satisfaction_forms import AssessmentReviewForm, AATReviewForm, QuestionReviewForm
from aat_main.models.account_model import AccountModel
from aat_main.models.assessment_models import Assessment
from aat_main.models.credit_model import CreditModel
from aat_main.models.question_models import Question
from aat_main.models.satisfaction_review_models import AssessmentReview, AATReview, QuestionReview
from aat_main.utils.authorization_helper import check_if_authorized

satisfaction_review_bp = Blueprint('satisfaction_review_bp', __name__, url_prefix='/review',
                                   template_folder='../views/satisfaction_reviews')

authorized_role = 'student'


# TODO add download as PDF button
@satisfaction_review_bp.route('/assessment/<assessment_id>', methods=['GET', 'POST'])
def assessment_review(assessment_id):
    check_if_authorized(authorized_role)

    form = AssessmentReviewForm()
    # reference https://stackoverflow.com/questions/14591202/how-to-make-a-radiofield-in-flask/14591681#14591681
    #  20 march
    if form.validate_on_submit():
        statement_response_map = json.dumps(
            {
                form.statement1.label.text: form.statement1.data,
                form.statement2.label.text: form.statement2.data
            }
        )

        AssessmentReview.create_review(current_user.id, assessment_id, statement_response_map,
                                       form.comment.data)

        # Insert credit event when a student review an assessment (Phoenix)
        credit_event = 'Give feedback to assessment(' + assessment_id + ')'
        CreditModel.insert_credit(current_user.id, 2, credit_event, assessment_id, 5, datetime.now())
        AccountModel().update_credit(current_user.id, 5)

        return redirect(url_for('satisfaction_review_bp.assessment_review_complete'))
    else:
        for error in form.errors.values():
            flash(error)

    assessment = Assessment.get_assessment_by_id(assessment_id)
    title = f'This is a review for {assessment.title}.'
    return render_template('satisfaction-review.html', assessment=assessment, form=form,
                           page_title=title)


@satisfaction_review_bp.route('/aat', methods=['GET', 'POST'])
def aat_review():
    check_if_authorized(authorized_role)
    if current_user.has_reviewed_aat_recently():
        days = current_user.get_days_until_next_aat_review()
        return render_template('wait-aat-review.html', num_of_days=days)

    form = AATReviewForm()
    if form.validate_on_submit():
        # TODO restructure program to allow for more statements to be added to forms and answers to be stored easily
        # reference 30 march. https://stackoverflow.com/questions/988228/convert-a-string-representation-of-a-dictionary-to-a-dictionary
        # reference 30 march. https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify
        statement_response_map = json.dumps(
            {
                form.statement1.label.text: form.statement1.data,
                form.statement2.label.text: form.statement2.data
            }
        )

        AATReview.create_review(current_user.id, statement_response_map, form.comment.data)

        # Insert credit event when a student review aat (Phoenix)
        credit_event = 'Give feedback to aat'
        CreditModel.insert_credit(current_user.id, 2, credit_event, 0, 5, datetime.now())
        AccountModel().update_credit(current_user.id, 5)
        print('update finished')
        flash('Thanks for reviewing automAATiq!')
        return redirect(url_for('index_bp.home'))
    else:
        for error in form.errors.values():
            flash(error)

    title = 'This is a review for automAATiq.'
    return render_template('satisfaction-review.html', form=form, page_title=title)


@satisfaction_review_bp.route('/question/<question_id>', methods=['GET', 'POST'])
def question_review(question_id):
    check_if_authorized(authorized_role)
    form = QuestionReviewForm()
    if form.validate_on_submit():
        statement_response_map = json.dumps(
            {
                form.statement1.label.text: form.statement1.data,
                form.statement2.label.text: form.statement2.data
            }
        )
        QuestionReview.create_review(current_user.id, question_id, statement_response_map,
                                     form.comment.data)

        # Insert credit event when a student review a question (Phoenix)
        credit_event = 'Give feedback to question(' + question_id + ')'
        CreditModel.insert_credit(current_user.id, 3, credit_event, question_id, 5, datetime.now())
        AccountModel().update_credit(current_user.id, 5)

        assessment_id = request.args.get('assessment_id')
        return redirect(url_for('satisfaction_review_bp.question_review_complete',
                                assessment_id=assessment_id))
    else:
        for error in form.errors.values():
            flash(error)

    question = Question.get_question_by_id(question_id)
    title = f'This is a review for the question: {question.description}'
    return render_template('satisfaction-review.html', question=question, form=form,
                           page_title=title)


@satisfaction_review_bp.route('/assessment/review-complete')
def assessment_review_complete():
    check_if_authorized(authorized_role)
    return render_template('assessment_review_complete.html')


@satisfaction_review_bp.route('/question/review-complete')
def question_review_complete():
    check_if_authorized(authorized_role)
    assessment_id = request.args.get('assessment_id')
    assessment = Assessment.get_assessment_by_id(assessment_id)
    return render_template('question_review_complete.html', assessment=assessment)
