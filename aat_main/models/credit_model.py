from sqlalchemy import MetaData, Table, func

from aat_main import db
from aat_main.models.assessment_models import Assessment
from aat_main.models.question_models import Question


class CreditModel(db.Model):
    __tablename__ = 'credit'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int
    account_id: int
    type: int, {0: formative, 1:summative, 2:feedback(assessment), 3:feedback(question) 4: collection}
    event: varchar
    target_id: int, (include assessment_id and question_id, and aat id is 0)
    credit: int
    time: datetime
    """

    @staticmethod
    def get_credit_by_account_id(account_id):
        return db.session.query(CreditModel).filter_by(account_id=account_id).order_by(CreditModel.time.desc()).all()

    @staticmethod
    def get_types_by_conditions(*conditions):
        return db.session.query(CreditModel.type).filter(*conditions).distinct().all()

    @staticmethod
    def get_assessment_events_by_conditions(*conditions):
        return db.session.query(CreditModel).join(Assessment, Assessment.id == CreditModel.target_id).filter(*conditions).all()

    @staticmethod
    def get_question_events_by_conditions(*conditions):
        return db.session.query(CreditModel).join(Question, Question.id == CreditModel.target_id).filter(*conditions).all()

    @staticmethod
    def get_credit_by_conditions(*conditions):
        return db.session.query(func.sum(CreditModel.credit)).filter(*conditions)

    @staticmethod
    def get_assessment_credit_by_conditions(*conditions):
        return db.session.query(func.sum(CreditModel.credit)).join(Assessment, Assessment.id == CreditModel.target_id).filter(*conditions)

    @staticmethod
    def get_question_credit_by_conditions(*conditions):
        return db.session.query(func.sum(CreditModel.credit)).join(Question, Question.id == CreditModel.target_id).filter(*conditions)

    @staticmethod
    def insert_credit(account_id, type, event, target_id, credit, time):
        db.session.add(CreditModel(account_id=account_id, type=type, event=event, target_id=target_id, credit=credit, time=time))
        db.session.commit()

    @staticmethod
    def check_credit(account_id, type, target_id):
        return db.session.query(CreditModel).filter_by(account_id=account_id, type=type, target_id=target_id).first()

    @staticmethod
    def check_credit_by_time(account_id, type, start_time, end_time):
        return db.session.query(CreditModel).filter(CreditModel.account_id == account_id, CreditModel.type == type, CreditModel.time.between(start_time, end_time)).all()
