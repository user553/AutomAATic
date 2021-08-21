from datetime import datetime

from flask import Blueprint, request
from flask_login import current_user

from aat_main.models.account_model import AccountModel
from aat_main.models.collection_model import CollectionModel
from aat_main.models.credit_model import CreditModel

collection_bp = Blueprint('collection_bp', __name__, static_folder='resources')


@collection_bp.route('/collection/', methods=['POST'])
def insert_collection():
    try:
        question_id = request.form.get('question_id')

        if not CollectionModel.get_collection(current_user.id, question_id):
            CollectionModel().insert_collection(current_user.id, question_id, datetime.now())
            credit_event = 'Collect question(' + question_id + ')'
            CreditModel.insert_credit(current_user.id, 4, credit_event, question_id, 5, datetime.now())
            AccountModel().update_credit(current_user.id, 5)
            return 'Success: Collection successful, credit +5'

        CollectionModel().insert_collection(current_user.id, question_id, datetime.now())
        return 'Success: Collection successful'
    except:
        return 'Fail: Collection failed'


@collection_bp.route('/collection/<int:question_id>', methods=['DELETE'])
def cancel_collection(question_id):
    try:
        CollectionModel().cancel_collection(current_user.id, question_id, datetime.now())
        return 'Success: Cancel successful'
    except:
        return 'Fail: Cancel failed'
