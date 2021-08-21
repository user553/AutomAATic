import json

from sqlalchemy import MetaData, Table

from aat_main import db
from aat_main.models.assessment_models import Assessment
from aat_main.models.question_models import Question


class CollectionModel(db.Model):
    __tablename__ = 'collection'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int, pk
    account_id: int
    question_id: int
    cancel: int, 1
    time: datetime
    """

    @staticmethod
    def get_collection(account_id, question_id):
        return db.session.query(CollectionModel).filter_by(account_id=account_id, question_id=question_id).first()

    def insert_collection(self, account_id, question_id, time):
        result = self.get_collection(account_id, question_id)
        if result is not None:
            result.cancel = 0
            result.time = time
        else:
            collection_model = CollectionModel(account_id=account_id, question_id=question_id, cancel=0, time=time)
            db.session.add(collection_model)
        db.session.commit()

    def cancel_collection(self, account_id, question_id, time):
        result = self.get_collection(account_id, question_id)
        if result is not None:
            result.cancel = 1
            result.time = time
        db.session.commit()

    def check_collection(self, account_id, question_id):
        result = self.get_collection(account_id, question_id)
        if result is None or result.cancel == 1:
            return False
        return True

    @staticmethod
    def get_collection_by_module(account_id, module):
        module_assessments = db.session.query(Assessment).filter_by(module=module).all()
        questions = []
        for assessment in module_assessments:
            for q in json.loads(assessment.questions):
                if Question.get_question_by_id(q) not in questions:
                    questions.append(Question.get_question_by_id(q))

        collection_questions = db.session.query(CollectionModel).filter_by(account_id=account_id, cancel=0).all()
        col_ids = []
        for col in collection_questions:
            col_ids.append(col.question_id)
        collections = []
        for q in questions:
            if q.id in col_ids:
                collections.append(q)
        return collections
