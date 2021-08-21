from flask_login import current_user
from sqlalchemy import MetaData, Table, or_
from sqlalchemy.exc import SQLAlchemyError

from aat_main import db
from aat_main.models.module_model import Module
from aat_main.models.satisfaction_review_models import QuestionReview


class Question(db.Model):
    __tablename__ = 'question'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)

    """
    id: int, auto_increment, primary
    name: varchar(128)
    description: varchar(256)
    module_code: varchar, foreign key
    type: int, formative-multiple choice:0; formative-fill in blank:1; summative:2
    feedback: text
    option: varchar(128)
    answer: varchar(128)
    release_time: datetime
    """

    @staticmethod
    def get_all():
        return db.session.query(Question).all()

    def get_question_by_id(id):
        return db.session.query(Question).get(id)

    @staticmethod
    def get_question_management_by_id(id):
        return db.session.query(Question).filter(Question.id == id).first()

    @staticmethod
    def get_question_by_module(module):
        return db.session.query(Question).filter(Question.module_code == module).all()

    @staticmethod
    def get_question_by_all_module():
        modules = current_user.get_enrolled_modules()
        conditions = [Question.module_code == mc.code for mc in modules]
        return db.session.query(Question).filter(or_(*conditions)).all()

    @staticmethod
    def create_question(name, description, module_code):
        db.session.add(Question(name=name, description=description, module_code=module_code))
        db.session.commit()

    @staticmethod
    def create_question_management(module_code, name, type, description, option, answer, feedback, time):
        db.session.add(
            Question(module_code=module_code, name=name, type=type, description=description,
                     option=option, answer=answer, feedback=feedback, release_time=time))
        db.session.commit()

    def update_question_management(self, module_code, name, type, description, option, answer, feedback, time,
                                   question_id):
        try:
            question = self.get_question_management_by_id(question_id)
            question.module_code = module_code
            question.name = name
            question.type = type
            question.description = description
            question.option = option
            question.answer = answer
            question.feedback = feedback
            question.release_time = time
            db.session.commit()
        except SQLAlchemyError:
            raise SQLAlchemyError

    @staticmethod
    def delete_question_by_id(id):
        db.session.query(Question).filter_by(id=id).delete()
        db.session.commit()

    def get_module(self):
        return db.session.query(
            Module
        ).filter_by(
            code=self.module_code
        ).first()

    def get_reviews(self):
        return db.session.query(
            QuestionReview
        ).filter_by(
            question_id=self.id
        ).all()
