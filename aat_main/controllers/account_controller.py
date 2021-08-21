import hashlib
import math
import time

import pandas
from flask import Blueprint, request, render_template, jsonify
from flask_login import current_user, login_required
from jinja2 import TemplateError
from sqlalchemy.exc import SQLAlchemyError

from aat_main.models.account_model import AccountModel
from aat_main.models.assessment_models import Assessment, AssessmentCompletion
from aat_main.models.collection_model import CollectionModel
from aat_main.models.credit_model import CreditModel
from aat_main.models.question_models import Question
from aat_main.utils.api_exception_helper import InterServerErrorException, NotFoundException
from aat_main.utils.base64_helper import Base64Helper
from aat_main.utils.serialization_helper import SerializationHelper

account_bp = Blueprint('account_bp', __name__, template_folder='../views/account_management')


@account_bp.before_request
@login_required
def before_request():
    pass


@account_bp.route('/account/')
def account_page():
    try:
        courses = current_user.get_enrolled_module_codes()
        return render_template('account_base.html', current_account=current_user, courses=courses,
                               student_stat_status=0)
    except TemplateError:
        raise NotFoundException()


@account_bp.route('/account/profile/', methods=['POST'])
def update_profile():
    try:
        avatar = request.form.get('avatar')
        name = request.form.get('name')
        password = request.form.get('password')
        profile = request.form.get('profile')

        if avatar.startswith("data:image/"):
            avatar = Base64Helper.base64_to_picture(avatar, 'avatars/' + current_user.email + '.jpg')
        else:
            avatar = current_user.avatar

        if password == '':
            password = current_user.password
        else:
            password = hashlib.md5(password.encode()).hexdigest()

        update_time = time.strftime('%Y-%m-%d %H:%M:%S')
        AccountModel.update_account(current_user.email, current_user.id, password, name, current_user.role, avatar,
                                    profile, update_time)
        return 'Success (Server) : Update profile successful'
    except SQLAlchemyError:
        raise InterServerErrorException()


@account_bp.route('/account/stat/attempt/<string:course>/')
def stat_attempt(course):
    return render_template('account_base.html', current_account=current_user, course=course, student_stat_status=1)


@account_bp.route('/account/stat/attempt/data/')
def stat_attempt_data():
    conditions = []
    if ('module' in request.args) and (request.args['module']):
        conditions.append(Assessment.module == request.args['module'])

    if ('type' in request.args) and (request.args['type']):
        if request.args['type'] == '0' or request.args['type'] == '1':
            conditions.append(Assessment.type == request.args['type'])

    if ('startDate' in request.args) and (request.args['startDate']):
        conditions.append(AssessmentCompletion.submit_time > request.args['startDate'])

    if ('endDate' in request.args) and (request.args['endDate']):
        conditions.append(AssessmentCompletion.submit_time < request.args['endDate'])

    if current_user.role == 'student':
        conditions.append(AssessmentCompletion.student_id == current_user.id)

    score = AssessmentCompletion.get_score_by_conditions(*conditions)
    return jsonify(SerializationHelper.model_to_list(score))


@account_bp.route('/account/stat/attainment/<string:course>/')
def stat_attainment(course):
    return render_template('account_base.html', current_account=current_user, course=course, student_stat_status=2)


@account_bp.route('/account/stat/attainment/data/')
def stat_attainment_data():
    conditions = []
    if ('module' in request.args) and (request.args['module']):
        conditions.append(Assessment.module == request.args['module'])

    if current_user.role == 'student':
        conditions.append(AssessmentCompletion.student_id == current_user.id)

    formative_scores = AssessmentCompletion.get_score_avg_by_conditions(*conditions, Assessment.type == '0')
    formative_scores = [score[0] for score in formative_scores]
    formative_df = pandas.DataFrame(formative_scores)
    if len(formative_scores) == 0:
        formative_score_avg = 0
    else:
        formative_score_avg = formative_df.mean().loc[0]

    summative_scores = AssessmentCompletion.get_score_avg_by_conditions(*conditions, Assessment.type == '1')
    summative_scores = [score[0] for score in summative_scores]
    summative_df = pandas.DataFrame(summative_scores)
    if len(summative_scores) == 0:
        summative_score_avg = 0
    else:
        summative_score_avg = summative_df.mean().loc[0]

    total_scores = formative_scores + summative_scores
    total_df = pandas.DataFrame(total_scores)
    if len(total_scores) == 0:
        know_level = [0, 0]
    elif len(total_scores) == 1:
        know_level = [total_scores[0], total_scores[0]]
    else:
        know_mean = total_df.mean().loc[0]
        know_std = total_df.std().loc[0]
        know_sigma = 1.96 * know_std / math.sqrt(len(total_scores))
        know_level = [round(know_mean - know_sigma, 2), round(know_mean + know_sigma, 2)]

    formative_accuracy = AssessmentCompletion.get_t1_accuracy_by_conditions(*conditions).scalar()
    if not formative_accuracy:
        formative_accuracy = 0
    summative_accuracy = AssessmentCompletion.get_t2_accuracy_by_conditions(*conditions).scalar()
    if not summative_accuracy:
        summative_accuracy = 0

    datas = [know_level, str(round(formative_score_avg, 2)), str(round(summative_score_avg, 2)), str(round(formative_accuracy, 0)), str(round(summative_accuracy, 0))]
    return jsonify(datas)


@account_bp.route('/account/stat/engagement/<string:course>/')
def stat_engagement(course):
    return render_template('account_base.html', current_account=current_user, course=course, student_stat_status=3)


@account_bp.route('/account/stat/engagement/data/')
def stat_engagement_data():
    # 0 formative credit
    for_con = []
    if ('module' in request.args) and (request.args['module']):
        for_con.append(Assessment.module == request.args['module'])
    if current_user.role == 'student':
        for_con.append(CreditModel.account_id == current_user.id)
        for_con.append(CreditModel.type == '0')
    for_credit = CreditModel.get_assessment_credit_by_conditions(*for_con).scalar()
    if for_credit:
        for_credit = int(for_credit)
    else:
        for_credit = 0

    # 1 summative credit
    sum_con = []
    if ('module' in request.args) and (request.args['module']):
        sum_con.append(Assessment.module == request.args['module'])
    if current_user.role == 'student':
        sum_con.append(CreditModel.account_id == current_user.id)
        sum_con.append(CreditModel.type == '1')
    sum_credit = CreditModel.get_assessment_credit_by_conditions(*sum_con).scalar()
    if sum_credit:
        sum_credit = int(sum_credit)
    else:
        sum_credit = 0

    # 2 assessment feedback credit
    ass_feed_con = []
    if ('module' in request.args) and (request.args['module']):
        ass_feed_con.append(Assessment.module == request.args['module'])
    if current_user.role == 'student':
        ass_feed_con.append(CreditModel.account_id == current_user.id)
        ass_feed_con.append(CreditModel.type == '2')
    ass_feed_credit = CreditModel.get_assessment_credit_by_conditions(*ass_feed_con).scalar()
    if ass_feed_credit:
        ass_feed_credit = int(ass_feed_credit)
    else:
        ass_feed_credit = 0

    # 3 question feedback credit
    ques_feed_con = []
    if ('module' in request.args) and (request.args['module']):
        ques_feed_con.append(Question.module_code == request.args['module'])
    if current_user.role == 'student':
        ques_feed_con.append(CreditModel.account_id == current_user.id)
        ques_feed_con.append(CreditModel.type == '3')
    ques_feed_credit = CreditModel.get_question_credit_by_conditions(*ques_feed_con).scalar()
    if ques_feed_credit:
        ques_feed_credit = int(ques_feed_credit)
    else:
        ques_feed_credit = 0

    # 4 collection credit
    col_con = []
    if ('module' in request.args) and (request.args['module']):
        col_con.append(Question.module_code == request.args['module'])
    if current_user.role == 'student':
        col_con.append(CreditModel.account_id == current_user.id)
        col_con.append(CreditModel.type == '4')
    col_credit = CreditModel.get_question_credit_by_conditions(*col_con).scalar()
    if col_credit:
        col_credit = int(col_credit)
    else:
        col_credit = 0

    # assessment_conditions = []
    # if ('module' in request.args) and (request.args['module']):
    #     assessment_conditions.append(Assessment.module == request.args['module'])
    # if current_user.role == 'student':
    #     assessment_conditions.append(CreditModel.account_id == current_user.id)
    #     assessment_conditions.append(CreditModel.type == '0')
    # assessment_credit = str(CreditModel.get_assessment_credit_by_conditions(*assessment_conditions).scalar())
    # if assessment_credit == 'None':
    #     assessment_credit = 0
    #
    # question_conditions = []
    # if ('module' in request.args) and (request.args['module']):
    #     question_conditions.append(Question.module_code == request.args['module'])
    # if current_user.role == 'student':
    #     question_conditions.append(CreditModel.account_id == current_user.id)
    #     question_conditions.append(CreditModel.type == '4')
    # question_credit = str(CreditModel.get_question_credit_by_conditions(*question_conditions).scalar())
    # if question_credit == 'None':
    #     question_credit = 0

    # credit_types = CreditModel.get_types_by_conditions(CreditModel.account_id == current_user.id)
    module_total = for_credit + sum_credit + ass_feed_credit + ques_feed_credit + col_credit
    credit_dic = [for_credit, sum_credit, ass_feed_credit, ques_feed_credit, col_credit, module_total]
    # credit_dic.update({5: int(assessment_credit) + int(question_credit)})

    # for credit_type in credit_types:
    #     if credit_type[0] == 0 or credit_type[0] == 1 or credit_type[0] == 2:
    #         credit = str(CreditModel.get_assessment_credit_by_conditions(*assessment_conditions, CreditModel.type == credit_type[0]).scalar())
    #     else:
    #         credit = str(CreditModel.get_question_credit_by_conditions(*question_conditions, CreditModel.type == credit_type[0]).scalar())
    #     if credit == 'None':
    #         credit = 0
    #     credit_dic.update({credit_type[0]: credit})
    return jsonify(credit_dic)


@account_bp.route('/account/stat/credit/data/<module>')
def stat_credit_data(module):
    # 0 formative events
    for_con = []
    for_con.append(Assessment.module == module)
    for_con.append(CreditModel.account_id == current_user.id)
    for_con.append(CreditModel.type == '0')
    for_events = CreditModel.get_assessment_events_by_conditions(*for_con)

    # 1 summative events
    sum_con = []
    sum_con.append(Assessment.module == module)
    sum_con.append(CreditModel.account_id == current_user.id)
    sum_con.append(CreditModel.type == '1')
    sum_events = CreditModel.get_assessment_events_by_conditions(*sum_con)

    # 2 assessment feedback events
    ass_feed_con = []
    ass_feed_con.append(Assessment.module == module)
    ass_feed_con.append(CreditModel.account_id == current_user.id)
    ass_feed_con.append(CreditModel.type == '2')
    ass_feed_events = CreditModel.get_assessment_events_by_conditions(*ass_feed_con)

    # 3 question feedback events
    ques_feed_con = []
    ques_feed_con.append(Question.module_code == module)
    ques_feed_con.append(CreditModel.account_id == current_user.id)
    ques_feed_con.append(CreditModel.type == '3')
    ques_feed_events = CreditModel.get_question_events_by_conditions(*ques_feed_con)

    # 4 collection events
    col_con = []
    col_con.append(Question.module_code == module)
    col_con.append(CreditModel.account_id == current_user.id)
    col_con.append(CreditModel.type == '4')
    col_events = CreditModel.get_question_events_by_conditions(*col_con)

    total_events = for_events + sum_events + ass_feed_events + ques_feed_events + col_events
    data = []
    for od in total_events:
        dic = {
            'id': od.id,
            'event': od.event,
            'credit': od.credit,
            'time': od.time
        }
        data.append(dic)
    return jsonify(data)


@account_bp.route('/account/stat/collection/data/<module>')
def stat_collection_data(module):
    collections = CollectionModel.get_collection_by_module(current_user.id, module)
    data = []
    type_dic = {0: 'Multiple choice', 1: 'Fill in blank', 2: 'Summative'}
    for od in collections:
        dic = {
            'id': od.id,
            'question': od.name,
            'description': od.description,
            'type': type_dic[od.type],
        }
        data.append(dic)
    return jsonify(data)
