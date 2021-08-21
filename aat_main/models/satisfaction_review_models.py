from datetime import datetime

from sqlalchemy import MetaData, Table

from aat_main import db


class AssessmentReview(db.Model):
    __tablename__ = 'assessment_review'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int, auto_increment
    student_id: int, foreign key
    assessment_id: int, foreign key
    statement_response_map: json
    comment: text
    """

    @staticmethod
    def create_review(student_id, assessment_id, statement_response_map, comment):
        db.session.add(AssessmentReview(student_id=student_id, assessment_id=assessment_id,
                                        statement_response_map=statement_response_map, comment=comment))
        db.session.commit()


class AATReview(db.Model):
    __tablename__ = 'aat_review'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int, auto_increment
    student_id: int, foreign key
    statement_response_map: json
    comment: text
    date: datetime, default=now()
    """

    @staticmethod
    def create_review(student_id, statement_response_map, comment):
        db.session.add(AATReview(student_id=student_id,
                                 statement_response_map=statement_response_map, comment=comment,
                                 date=datetime.utcnow()))
        db.session.commit()

    @staticmethod
    def get_all_reviews():
        return db.session.query(AATReview).all()


class QuestionReview(db.Model):
    __tablename__ = 'question_review'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int, auto_increment
    student_id: int, foreign key
    question_id: int foreign key
    statement_response_map: json
    comment: text
    """

    @staticmethod
    def create_review(student_id, question_id, statement_response_map, comment):
        db.session.add(QuestionReview(student_id=student_id, question_id=question_id,
                                      statement_response_map=statement_response_map, comment=comment))
        db.session.commit()
