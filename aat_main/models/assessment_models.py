# from ast import literal_eval
import ast
from datetime import datetime

from sqlalchemy import MetaData, Table, func
from sqlalchemy.exc import SQLAlchemyError

from aat_main import db
from aat_main.models.question_models import Question
from aat_main.models.satisfaction_review_models import AssessmentReview


class Assessment(db.Model):
    __tablename__ = 'assessment'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int, auto_increment, primary
    title: varchar(64)
    description: text
    type: int, formative: 0; summative: 1
    module: varchar(8), foreign key references module(code)
    questions: varchar(256)
    count_in: int(3)
    attempt: int(3)
    availability_date: datetime
    due_date: datetime
    timelimit: int, default(0)
    time_created: datetime, default now()
    """

    # TODO maybe add percentage completed on 'Available Assessments' page to get the distinction
    #  criteria for going beyond expectations

    @staticmethod
    def get_all():
        return db.session.query(Assessment).all()

    @staticmethod
    def get_assessment_by_id(id):
        return db.session.query(Assessment).get(id)

    def get_reviews(self):
        return db.session.query(AssessmentReview).filter_by(assessment_id=self.id).all()

    def convert_datetime(date, time):
        return str(date) + " " + str(time)

    @staticmethod
    def create_assessment(title, questions, description, module, type, count_in, attempt, start_datetime, end_datetime,
                          timelimit, time):
        try:
            # question_string = generate_question_string(questions)
            db.session.add(
                Assessment(title=title, questions=questions, description=description, module=module, type=type,
                           count_in=count_in, attempt=attempt, availability_date=start_datetime,
                           due_date=end_datetime, timelimit=timelimit, time_created=time))
            db.session.commit()
        except SQLAlchemyError:
            raise SQLAlchemyError

    @staticmethod
    def update_assessment(title, questions, description, start_datetime, end_datetime, timelimit, count_in, attempt, assessment_id):
        try:
            assessment = Assessment.query.filter_by(id=assessment_id).first()
            assessment.title = title
            assessment.questions = questions
            assessment.description = description
            assessment.availability_date = start_datetime
            assessment.due_date = end_datetime
            assessment.timelimit = timelimit
            assessment.count_in = count_in
            assessment.attempt = attempt
            db.session.commit()
        except SQLAlchemyError:
            raise SQLAlchemyError

    @staticmethod
    def delete_assessment(assessment_id):
        try:
            assessment = Assessment.query.filter_by(id=assessment_id).first()
            db.session.delete(assessment)
            db.session.commit()
        except SQLAlchemyError:
            raise SQLAlchemyError

    @staticmethod
    def get_all_current(time):
        return db.session.query(Assessment).filter(Assessment.type == 0, Assessment.due_date > time).all()

    @staticmethod
    def get_all_pass(time):
        return db.session.query(Assessment).filter(Assessment.type == 0, Assessment.due_date < time).all()

    @staticmethod
    def get_all_current_by_module(module, time):
        return db.session.query(Assessment).filter(Assessment.type == 0, Assessment.module == module, Assessment.due_date > time).all()

    @staticmethod
    def get_all_pass_by_module(module, time):
        return db.session.query(Assessment).filter(Assessment.type == 0, Assessment.module == module, Assessment.due_date < time).all()

    @staticmethod
    def delete_assessment_by_id(id):
        try:
            db.session.query(Assessment).filter_by(id=id).delete()
            db.session.commit()
        except SQLAlchemyError:
            return 'Server error'

    def get_questions(self):
        questions = db.session.query(Assessment.questions).filter_by(id=self.id).first()
        questions_ids = ast.literal_eval(questions[0])

        return db.session.query(Question).filter(Question.id.in_(questions_ids)).all()

    # @staticmethod
    # def is_due(assessment):
    #     return assessment.availability_date < datetime.now() < assessment.due_date

    @staticmethod
    def is_due(availability_date, due_date):
        return availability_date < datetime.now() < due_date


class AssessmentCompletion(db.Model):
    __tablename__ = 'assessment_completion'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int, pk, auto_increment
    student_id: int, foreign key, references account(id)
    assessment_id: int, foreign key, references assessment(id)
    results: json (dict of question.id + true/false or quest ans)
    t1_accuracy: int
    t2_accuracy: int
    mark: int
    submit_time: datetime
    """

    @staticmethod
    def create_assessment_completion(student_id, assessment_id, results, mark, t1_accuracy, t2_accuracy, submit_time):
        try:
            db.session.add(AssessmentCompletion(student_id=student_id, assessment_id=assessment_id, results=results, t1_accuracy=t1_accuracy, t2_accuracy=t2_accuracy, mark=mark,
                                                submit_time=submit_time))
            db.session.commit()
        except SQLAlchemyError:
            raise SQLAlchemyError

    @staticmethod
    def get_completed_assessments_by_user_id(id):
        return db.session.query(AssessmentCompletion).filter_by(student_id=id).distinct().all()

    @staticmethod
    def get_attempts_by_assessment(account_id, assessment_id):
        return db.session.query(AssessmentCompletion).filter_by(student_id=account_id, assessment_id=assessment_id).all()

    @staticmethod
    def get_results_by_id(stu_id, ass_id):
        return db.session.query(AssessmentCompletion).filter(AssessmentCompletion.student_id == 'stu_id', AssessmentCompletion.assessment_id == 'ass_id').all()

    @staticmethod
    def get_score_by_conditions(*conditions):
        return db.session.query(AssessmentCompletion).join(Assessment, AssessmentCompletion.assessment_id == Assessment.id).filter(*conditions).all()

    @staticmethod
    def get_score_avg_by_conditions(*conditions):
        return db.session.query(AssessmentCompletion.mark).join(Assessment, AssessmentCompletion.assessment_id == Assessment.id).filter(*conditions).all()

    @staticmethod
    def get_t1_accuracy_by_conditions(*conditions):
        return db.session.query(func.avg(AssessmentCompletion.t1_accuracy)).join(Assessment, AssessmentCompletion.assessment_id == Assessment.id).filter(*conditions)

    @staticmethod
    def get_t2_accuracy_by_conditions(*conditions):
        return db.session.query(func.avg(AssessmentCompletion.t2_accuracy)).join(Assessment, AssessmentCompletion.assessment_id == Assessment.id).filter(*conditions)
