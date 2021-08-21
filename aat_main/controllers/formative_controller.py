import json
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from jinja2 import TemplateError

from aat_main.models.assessment_models import Assessment
from aat_main.models.question_models import Question
from aat_main.utils.api_exception_helper import NotFoundException

formative_blueprint = Blueprint('formative_blueprint', __name__, template_folder='../views/formative')


@formative_blueprint.route('/assessments/assessments_management/formative/', methods=['GET', 'POST'])
def formative():
    # form = assessment_form()
    # if form.validate_on_submit():
    #     Assessment.create_assessment(form.title.data)
    #     return redirect(url_for('assessment_bp.assessments'))
    # form = module_choice_form()
    # message = 'Nothing Now'
    # if request.method == "POST":
    #     if form.validate_on_submit():
    #         # Gets module code
    #         module_code = form.module.data.split(':')[0]
    #         message = module_code
    #
    #         return message
    modules = current_user.get_enrolled_modules()
    return render_template("formative.html", modules=modules)


@formative_blueprint.route('/assessments/assessments_management/formative/<string:status>/<string:module>')
def assessment_data(status, module):
    try:
        current_time = datetime.now()
        if status == 'current':
            if module == 'Please Choose a Module':
                origin_data = Assessment.get_all_current(current_time)
            else:
                origin_data = Assessment.get_all_current_by_module(module, current_time)
        else:
            if module == 'Please Choose a Module':
                origin_data = Assessment.get_all_pass(current_time)
            else:
                origin_data = Assessment.get_all_pass_by_module(module, current_time)

        data = []
        for od in origin_data:
            dic = {
                'id': od.id,
                'title': od.title,
                'release_time': od.availability_date,
                'deadline': od.due_date
            }
            data.append(dic)
        # if request.method == 'GET':
        #     info = request.values
        #     limit = info.get('limit', 10)
        #     offset = info.get('offset', 0)
        # return jsonify({
        #     'total': len(data),
        #     'rows': data[int(offset):(int(offset) + int(limit))]
        # })
        return jsonify(data)
    except:
        return 'server error'


@formative_blueprint.route('/assessments/assessments_management/formative/<assessment_id>')
def assessment_questions(assessment_id):
    try:
        assessment = Assessment.get_assessment_by_id(assessment_id)
        if assessment.questions:
            question_ids = json.loads(assessment.questions)
        origin_data = []
        for question_id in question_ids:
            origin_data.append(Question.get_question_management_by_id(int(question_id)))

        data = []
        type_dic = {0: 'Multiple choice', 1: 'Fill in blank', 2: 'Summative'}
        for od in origin_data:
            dic = {
                'id': od.id,
                'module': od.module_code,
                'question': od.name,
                'description': od.description,
                'type': type_dic[od.type],
                'option': od.option,
                'answer': od.answer,
                'feedback': od.feedback,
                'release_time': od.release_time
            }
            data.append(dic)

        # if request.method == 'GET':
        #     info = request.values
        #     limit = info.get('limit', 10)
        #     offset = info.get('offset', 0)
        # return jsonify({
        #     'total': len(data),
        #     'rows': data[int(offset):(int(offset) + int(limit))]
        # })
        return jsonify(data)
    except:
        return 'Server error'


@formative_blueprint.route('/assessments/assessments_management/formative/create/', methods=['POST'])
def create_assessment_data():
    try:
        # Assessment.create_assessment(1, 1, 1, 1, 1, 1, 1, datetime.now(), datetime.now(), 1)
        assessment = {}
        for k, v in request.form.items():
            assessment[k] = v
        formativeTitle = assessment['formativeTitle']
        releaseTime = datetime.fromisoformat(assessment['releaseTime'])
        dueDate = datetime.fromisoformat(assessment['dueDate'])
        countIn = int(assessment['countIn'])
        attemptTime = int(assessment['attemptTime'])
        timeLimit = int(assessment['timeLimit'])
        description = assessment['description']
        module = assessment['module']

        Assessment.create_assessment(formativeTitle, '', description, module, 0, countIn, attemptTime, releaseTime,
                                     dueDate, timeLimit, datetime.now())
        # Assessment.create_assessment(formativeTitle, '', description, module, 0, countIn, attemptTime, datetime.now(),
        #                              datetime.now(), timeLimit, datetime.now())
        return 'create successful'
    except:
        return 'Server error'


@formative_blueprint.route('/assessments/assessments_management/formative/delete/', methods=['POST'])
def delete_assessment_data():
    try:
        for k, v in request.form.items():
            Assessment.delete_assessment_by_id(k)
        return 'delete successful'
    except:
        return 'Server error'


@formative_blueprint.route('/assessments/assessments_management/formative/edit/<id>', methods=['GET'])
def edit_assessment(id):
    try:
        current_assessment = Assessment.get_assessment_by_id(id)
        return render_template("formative_detail.html", current_assessment=current_assessment)
    except TemplateError:
        return 'Server error'


@formative_blueprint.route('/assessments/assessments_management/formative/update/<id>', methods=['POST'])
def update_assessment_data(id):
    try:
        ass = Assessment.get_assessment_by_id(id)
        # Assessment.create_assessment(1, 1, 1, 1, 1, 1, 1, datetime.now(), datetime.now(), 1)
        assessment = {}
        for k, v in request.form.items():
            assessment[k] = v
        formativeTitle = assessment['formativeTitle']
        releaseTime = datetime.fromisoformat(assessment['releaseTime'])
        dueDate = datetime.fromisoformat(assessment['dueDate'])
        countIn = int(assessment['countIn'])
        attemptTime = int(assessment['attemptTime'])
        timeLimit = int(assessment['timeLimit'])
        description = assessment['description']

        Assessment.update_assessment(formativeTitle, ass.questions, description,
                                     releaseTime, dueDate, timeLimit, countIn, attemptTime,
                                     ass.id)
        return 'update successful'
    except:
        return 'Server error'


@formative_blueprint.route('/assessments/assessments_management/formative/question/add/<assessment_id>',
                           methods=['POST'])
def add_question_to_assessment(assessment_id):
    try:
        assessment = Assessment.get_assessment_by_id(assessment_id)
        assessment_questions = []
        if assessment.questions:
            assessment_questions = json.loads(assessment.questions)
        if len(assessment_questions) == 1 and assessment_questions[0] == '':
            assessment_questions = []

        all_module_questions = Question.get_question_by_module(assessment.module)
        module_question_ids = []
        for module_question in all_module_questions:
            module_question_ids.append(str(module_question.id))
        for k, v in request.form.items():
            if k in module_question_ids:
                if k not in assessment_questions:
                    assessment_questions.append(str(k))
        assessment_questions = json.dumps(assessment_questions)
        Assessment.update_assessment(assessment.title, assessment_questions, assessment.description,
                                     assessment.availability_date, assessment.due_date, assessment.timelimit, assessment.count_in, assessment.attempt,
                                     assessment_id)
        return 'added successful'
    except:
        return 'Server error'


@formative_blueprint.route('/assessments/assessments_management/formative/question/delete/<assessment_id>',
                           methods=['POST'])
def delete_question_from_assessment(assessment_id):
    try:
        assessment = Assessment.get_assessment_by_id(assessment_id)
        assessment_questions = json.loads(assessment.questions)
        if len(assessment_questions) == 1 and assessment_questions[0] == '':
            assessment_questions = []
        for k, v in request.form.items():
            if k in assessment_questions:
                assessment_questions.remove(str(k))
        assessment_questions = json.dumps(assessment_questions)
        Assessment.update_assessment(assessment.title, assessment_questions, assessment.description,
                                     assessment.availability_date, assessment.due_date, assessment.timelimit,
                                     assessment.count_in, assessment.attempt,
                                     assessment_id)
        return 'delete successful'
    except:
        return 'Server error'


@formative_blueprint.route('/course/assessment/')
def course_assessment_page():
    try:
        return render_template('assessment.html')
    except TemplateError:
        raise NotFoundException()

# @formative_blueprint.errorhandler(404)
# def catch_http_exception(e):
#     if isinstance(e, HTTPException):
#         api_exception = APIException(e.code, e.description)
#     else:
#         api_exception = InterServerErrorException()
#     return render_template('error.html', api_exception=api_exception)
