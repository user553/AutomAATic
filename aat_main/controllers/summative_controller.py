import datetime
import json
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from jinja2 import TemplateError

from aat_main import db
from aat_main.forms.summative_forms import assessment_form, summative_edit_form
from aat_main.models.assessment_models import Assessment
from aat_main.models.enrolment_models import ModuleEnrolment
from aat_main.models.module_model import Module
from aat_main.models.question_models import Question
from aat_main.utils.api_exception_helper import NotFoundException

summative_blueprint = Blueprint('summative_blueprint', __name__, template_folder='../views/summative')


@summative_blueprint.route('/assessments/assessment_management/summative')
def summative():
    assessments = Assessment.get_all()
    return render_template("summative.html", assessments=assessments)


@summative_blueprint.route('/assessments/assessment_management/summative/create', methods=['GET', 'POST'])
def summative_create():
    questions = Question.get_all()
    form = assessment_form()
    module_db = Module.get_all()
    # https://www.youtube.com/watch?v=I2dJuNwlIH0&ab_channel=PrettyPrinted
    module_choices = [(mod.code, (f'{mod.code}  :  {mod.name}')
                       ) for mod in db.session.query(
        Module).join(ModuleEnrolment, Module.code == ModuleEnrolment.module_code
                     ).filter(ModuleEnrolment.account_id == current_user.id).all()]
    module_choices.insert(0, ("Please Choose a Module", "Please Choose a Module"))
    form.module.choices = module_choices

    # To validate modules lecturer is enroled on and check questions + gets question ids (CLEAN THIS UP)
    valid_modules = [(mod.code
                      ) for mod in db.session.query(
        Module).join(ModuleEnrolment, Module.code == ModuleEnrolment.module_code
                     ).filter(ModuleEnrolment.account_id == current_user.id).all()]

    valid_questions = []
    question_id = []
    for question in questions:
        if question.module_code in valid_modules:
            question_id.append(question.id)
            valid_questions.append(question)

    question_id = json.dumps(question_id)

    if request.method == "POST":
        if form.validate_on_submit():
            added_questions = []
            # Checks if checkbox is active. If yes, adds value to added questions.
            for question in questions:
                question_id = request.form.get(str(question.id))
                if question_id:
                    added_questions.append(question_id)

            module_code = form.module.data.split()
            module_code = module_code[0]

            # Convert Datetime's
            start_datetime = Assessment.convert_datetime(form.start_date.data, form.start_time.data)
            end_datetime = Assessment.convert_datetime(form.end_date.data, form.end_time.data)

            added_questions = json.dumps(added_questions)
            type = 1
            count_in = 0
            attempts = 1
            Assessment.create_assessment(form.title.data, added_questions, form.description.data, module_code, type, count_in, attempts,
                                         start_datetime, end_datetime, form.timelimit.data, datetime.now())
            return redirect(url_for('assessment_bp.assessments'))
    return render_template("summative_create.html", form=form, questions=valid_questions, modules=module_choices, question_id=question_id, valid_modules=valid_modules)
    # try:
    #     return render_template('summative.html')
    # except TemplateError:
    #     raise NotFoundException()


@summative_blueprint.route('/assessments/assessment_management/summative/<int:assessment_id>', methods=['GET', 'POST'])
def summative_edit(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    form = summative_edit_form()
    questions = Question.get_all()

    added_questions = assessment.questions

    availdate = assessment.availability_date
    startdate = availdate.date()
    starttime = availdate.strftime("%H:%M:%S")

    duedate = assessment.due_date
    enddate = duedate.date()
    endtime = duedate.strftime("%H:%M:%S")

    if request.method == "POST":
        if form.validate_on_submit():
            added_questions = []
            # Checks if checkbox is active. If yes, adds value to added questions.
            for question in questions:
                question_id = request.form.get(str(question.id))
                if question_id:
                    added_questions.append(question_id)

            added_questions = json.dumps(added_questions)

            # Convert Datetime's

            start_datetime = Assessment.convert_datetime(request.form.get("start_date"), request.form.get("start_time"))
            end_datetime = Assessment.convert_datetime(request.form.get("end_date"), request.form.get("end_time"))

            title = request.form.get("title_form")

            timelimit = request.form.get("timelimit_form")

            description = request.form.get("description_form")

            assessment_id = assessment.id

            Assessment.update_assessment(title, added_questions, description, start_datetime, end_datetime, timelimit, assessment.count_in, 1, assessment_id)
            return redirect(url_for('assessment_bp.assessments'))

    return render_template("summative_edit.html", assessment=assessment, form=form,
                           questions=questions, startdate=startdate, starttime=starttime,
                           enddate=enddate, endtime=endtime, added_questions=added_questions)


@summative_blueprint.route('/delete/<int:assessment_id>/<action>')
def summative_delete_action(assessment_id, action):
    assessment = Assessment.query.filter_by(id=assessment_id).first_or_404()

    if action == 'delete':
        assessment.delete_assessment(assessment_id)
        db.session.commit()

    return redirect(request.referrer)


@summative_blueprint.route('/course/assessment/')
def course_assessment_page():
    try:
        return render_template('assessment.html')
    except TemplateError:
        raise NotFoundException()

# @summative_blueprint.errorhandler(404)
# def catch_http_exception(e):
#     if isinstance(e, HTTPException):
#         api_exception = APIException(e.code, e.description)
#     else:
#         api_exception = InterServerErrorException()
#     return render_template('error.html', api_exception=api_exception
