from sqlalchemy import MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

from aat_main import db
from aat_main.utils.api_exception_helper import InterServerErrorException


class MultipleChoice(db.Model):
    __tablename__ = 'MultipleChoice'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)

    @staticmethod
    def search_question_by_id(id):
        try:
            return db.session.query(MultipleChoice).filter_by(id=id).first()
        except SQLAlchemyError:
            return InterServerErrorException()

    @staticmethod
    def create_question(id, question, answer, options):
        try:
            db.session.add(MultipleChoice(id=id, question=question, answer=answer, options=options))
            db.session.commit()
        except SQLAlchemyError:
            return InterServerErrorException()

    def update_question(self, id, question, answer, options):
        try:
            self.search_question_by_id(id).update({'question': question, 'answer': answer, 'options': options})
            db.session.commit()
        except SQLAlchemyError:
            return InterServerErrorException()

    def delete_question(self, id):
        try:
            self.search_question_by_id(id).delete()
            db.session.commit()
        except SQLAlchemyError:
            return InterServerErrorException()
