import json
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required

from aat_main.forms.complete_assessment_form import complete_assessment_form
from aat_main.models.account_model import AccountModel
from aat_main.models.assessment_models import Assessment, AssessmentCompletion
from aat_main.models.collection_model import CollectionModel
from aat_main.models.credit_model import CreditModel
from aat_main.models.question_models import Question

assessment_bp = Blueprint('assessment_bp', __name__, url_prefix='/assessments', template_folder='../views')


# Make login required for all endpoints within blueprint
@assessment_bp.before_request
@login_required
def before_request():
    pass


@assessment_bp.route('/')
def assessments():
    if current_user.role == 'student':
        return render_template('assessments_students.html')
    elif current_user.role == 'lecturer':
        assessments = current_user.get_available_assessments_lecturer()
        return render_template('assessments_lecturers.html', assessments=assessments)

    return render_template('base.html')


@assessment_bp.route('/available/')
def available_assessments():
    if current_user.role == 'student':
        assessments = current_user.get_available_assessments_student()
        completed = AssessmentCompletion.get_completed_assessments_by_user_id(current_user.id)

        valid_assessments = []

        for assessment in assessments:
            if not any(comp.assessment_id == assessment.id for comp in completed):
                valid_assessments.append(assessment)

        for complete in completed:
            attempts = len(AssessmentCompletion.get_attempts_by_assessment(current_user.id, complete.assessment_id))
            original_assessment = Assessment.get_assessment_by_id(complete.assessment_id)
            if original_assessment.attempt == -1 and original_assessment not in valid_assessments:
                valid_assessments.append(original_assessment)
                continue
            if attempts < original_assessment.attempt and original_assessment not in valid_assessments:
                original_assessment.attempt -= attempts
                valid_assessments.append(original_assessment)
                print(original_assessment.attempt)

        return render_template('available_assessments.html', assessments=valid_assessments)

    return redirect(url_for('assessment_bp.assessments'))


@assessment_bp.route('/completed/')
def completed_assessments():
    assessments = current_user.get_completed_assessments()
    return render_template('completed_assessments.html', assessments=assessments)


@assessment_bp.route('/<assessment_id>/questions')
def assessment_questions(assessment_id):
    assessment = Assessment.get_assessment_by_id(assessment_id)
    questions = assessment.get_questions()
    return render_template('assessment_questions.html', assessment=assessment, questions=questions)


# Assessments Management page (Matt)
@assessment_bp.route('/manage')
@login_required
def assessments_management():
    assessments = Assessment.get_all()
    return render_template('assessments_management.html', assessments=assessments)


@assessment_bp.route('/start/<assessment_id>')
def start_assessment(assessment_id):
    attempts = len(AssessmentCompletion.get_attempts_by_assessment(current_user.id, assessment_id))
    assessment = Assessment.get_assessment_by_id(assessment_id)
    assessment.attempt -= attempts
    assessment_questions = []
    if assessment.questions:
        assessment_questions = json.loads(assessment.questions)
    question_num = len(assessment_questions)
    return render_template('assessment_start.html', assessment=assessment, question_num=question_num)


@assessment_bp.route('/questions/<assessment_id>', methods=['GET', 'POST'])
def answer_questions(assessment_id):
    form = complete_assessment_form()
    assessment = Assessment.get_assessment_by_id(assessment_id)
    assessment_questions = []
    if assessment.questions:
        assessment_questions = json.loads(assessment.questions)
    questions = []
    question_options = {}
    total_mark = 0
    time = assessment.timelimit

    for question in assessment_questions:
        questions.append(Question.get_question_by_id(int(question)))

    # Generates options for each question (Try using json.load. See if that works. This does but its inefficient)
    for quest in questions:
        temp_options = []
        if quest.option != "" or None:
            q_string = quest.option
            options = (q_string).split("}{")

            for opt in options:
                opt = opt.replace("{", "")
                opt = opt.replace("}", "")
                opt = opt.split(":")
                temp_options.append(opt[1])
        question_options[quest.id] = temp_options

    answers = {}
    if request.method == "POST":
        t1_mark = 0
        t1_count = 0
        t2_mark = 0
        t2_count = 0
        for quest in questions:
            if quest.type == 0:
                t1_count += 1
                options = question_options[quest.id]
                if request.form.get(str(quest.id)) == quest.answer:
                    t1_mark += 1
                for opt in options:
                    value = request.form.get(str(quest.id))
                    if value:
                        answers[quest.id] = value

            elif quest.type == 1:
                t2_count += 1
                value = request.form.get(str(quest.id))
                answers[quest.id] = value
                if value == quest.answer:
                    t2_mark += 1

        total_mark = t1_mark + t2_mark
        if t1_count == 0:
            t1_accuracy = 0
        else:
            t1_accuracy = round(t1_mark / t1_count, 2) * 100

        if t2_count == 0:
            t2_accuracy = 0
        else:
            t2_accuracy = round(t2_mark / t2_count, 2) * 100
        answers_submit = json.dumps(answers)
        AssessmentCompletion.create_assessment_completion(current_user.id, assessment.id, answers_submit, total_mark,
                                                          t1_accuracy, t2_accuracy, datetime.now())

        # Insert credit event when a student finish an assessment (Phoenix)
        credit_event = 'Finish assessment(' + str(assessment.id) + ')'
        CreditModel.insert_credit(current_user.id, assessment.type, credit_event, assessment.id, 5, datetime.now())
        AccountModel().update_credit(current_user.id, 5)

        return redirect(url_for('assessment_bp.assessment_feedback', assessment_id=assessment.id))

    return render_template('question_in_assessment.html', assessment=assessment, questions=questions,
                           question_options=question_options, form=form, time=time)


@assessment_bp.route('/feedback/<assessment_id>')
def assessment_feedback(assessment_id):
    results = AssessmentCompletion.get_completed_assessments_by_user_id(current_user.id)
    assessment = Assessment.get_assessment_by_id(assessment_id)
    assessment_questions = json.loads(assessment.questions)
    questions = []
    question_options = {}
    valid_result = {}
    mark = 0
    outof = 0
    time_now = datetime.now()

    for question in assessment_questions:
        questions.append(Question.get_question_by_id(int(question)))

    for quest in questions:
        outof += 1
        temp_options = []
        if quest.option != "" or None:
            q_string = quest.option
            options = (q_string).split("}{")

            for opt in options:
                opt = opt.replace("{", "")
                opt = opt.replace("}", "")
                opt = opt.split(":")
                temp_options.append(opt[1])
        question_options[quest.id] = temp_options

    for res in results:
        if res.assessment_id == assessment.id:
            valid_result = json.loads(res.results)
            mark = res.mark

    if assessment.type == 1:
        if assessment.due_date > time_now:
            return render_template('feedback_not_available.html', assessment=assessment)
        else:
            return render_template('submitted_assessment.html',
                                   questions=questions, assessment=assessment,
                                   question_options=question_options, results=valid_result,
                                   mark=mark, outof=outof, collection_instance=CollectionModel())
    if assessment.type == 0:
        return render_template('submitted_assessment.html',
                               questions=questions, assessment=assessment,
                               question_options=question_options, results=valid_result,
                               mark=mark, outof=outof, collection_instance=CollectionModel())
