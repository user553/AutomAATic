from ast import literal_eval
from datetime import datetime

from flask_login import UserMixin, current_user
from sqlalchemy import MetaData, Table, and_

from aat_main import db, login_manager
from aat_main.models.assessment_models import Assessment, AssessmentCompletion
from aat_main.models.enrolment_models import ModuleEnrolment
from aat_main.models.module_model import Module
from aat_main.models.question_models import Question
from aat_main.models.satisfaction_review_models import AssessmentReview, AATReview, QuestionReview


class AccountModel(db.Model, UserMixin):
    __tablename__ = 'account'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int, primary key, auto_increment
    email: varchar(128)
    password: varchar(128)
    name: varchar(64)
    role: varchar(16) (either student, lecturer, or admin)
    avatar: varchar(64)
    profile: tinytext(0)
    credit: int
    time: datetime
    """

    DAYS_BETWEEN_AAT_REVIEWS = 7

    @staticmethod
    def search_all():
        return db.session.query(AccountModel).all()

    @staticmethod
    def search_account_by_id(id):
        return db.session.query(AccountModel).get(id)

    @staticmethod
    def search_account_by_email(email):
        return db.session.query(AccountModel).filter_by(email=email).first()

    @staticmethod
    def create_account(id, email, password, name):
        db.session.add(AccountModel(id=id, email=email, password=password, name=name))
        db.session.commit()

    @staticmethod
    def update_account(email, id, password, name, role, avatar, profile, time):
        db.session.query(AccountModel).filter_by(email=email).update(
            {'id': id, 'password': password, 'name': name, 'role': role, 'avatar': avatar, 'profile': profile,
             'time': time})
        db.session.commit()

    def delete_account(self, id):
        self.search_account_by_id(id).delete()
        db.session.commit()

    def get_available_assessments_student(self):
        module_codes = self.get_enrolled_module_codes()
        completed = self.get_completed_assessments()

        time_now = str(datetime.now())

        return db.session.query(
            Assessment
        ).filter(
            and_(
                Assessment.module.in_(module_codes),
                and_(
                    Assessment.availability_date <= time_now,
                    time_now <= Assessment.due_date
                )
            )
        ).all()

    def get_completed_assessments(self):
        return db.session.query(
            Assessment
        ).join(
            AssessmentCompletion,
            Assessment.id == AssessmentCompletion.assessment_id
        ).filter(
            AssessmentCompletion.student_id == self.id
        ).all()

    def has_reviewed_assessment(self, assessment_id):
        return db.session.query(
            AssessmentReview
        ).filter(
            and_(
                AssessmentReview.student_id == self.id,
                AssessmentReview.assessment_id == assessment_id
            )
        ).first()

    def has_reviewed_all_questions(self, assessment_id):
        assessment = db.session.query(Assessment).filter_by(id=assessment_id).first()
        questions = assessment.get_questions()
        reviewed_questions = db.session.query(
            Question
        ).join(
            QuestionReview,
            Question.id == QuestionReview.question_id
        ).filter(
            QuestionReview.student_id == self.id
        ).all()
        return all(q in reviewed_questions for q in questions)

    def get_completed_questions(self):
        # TODO check if this works after changes to tables are made
        completed_assessments = db.session.query(
            Assessment
        ).join(
            AssessmentCompletion,
            AssessmentCompletion.assessment_id == Assessment.id
        ).filter(
            AssessmentCompletion.student_id == self.id
        ).all()

        completed_question_ids = {}
        for assessment in completed_assessments:
            question_set = literal_eval(assessment.questions)
            completed_question_ids.update(question_set)

        return db.session.query(
            Question
        ).filter(
            Question.id.in_(completed_question_ids)
        )

        # return db.session.query(Question).all()

    def has_reviewed_question(self, id):
        return db.session.query(
            QuestionReview
        ).filter(
            and_(
                QuestionReview.student_id == self.id,
                QuestionReview.question_id == id
            )
        ).first()

    def get_last_aat_review(self):
        return db.session.query(
            AATReview
        ).filter_by(
            student_id=self.id
        ).order_by(
            AATReview.date.desc()
        ).first()

    # reference https://stackoverflow.com/questions/46046136/find-out-if-a-date-is-more-than-30-days-old/46046182#46046182
    # 21 March
    def has_reviewed_aat_recently(self):
        if (last_review := self.get_last_aat_review()) is None:
            return False
        else:
            time_elapsed = datetime.now() - last_review.date
            return time_elapsed.days < self.DAYS_BETWEEN_AAT_REVIEWS

    def get_days_until_next_aat_review(self):
        last_review_date = self.get_last_aat_review().date
        time_elapsed = datetime.now() - last_review_date
        # The min() is needed below because time_elapsed.days==-1 immediately after the review is made, making days
        # remaining until next review == 8
        return min(self.DAYS_BETWEEN_AAT_REVIEWS, self.DAYS_BETWEEN_AAT_REVIEWS - time_elapsed.days)

    def get_enrolled_modules(self):
        return db.session.query(
            Module
        ).join(
            ModuleEnrolment,
            ModuleEnrolment.module_code == Module.code
        ).filter(
            ModuleEnrolment.account_id == self.id
        ).all()

    def get_enrolled_module_codes(self):
        # reference 14 April https://stackoverflow.com/questions/11530196/flask-sqlalchemy-query-specify-column-names
        # module_codes = db.session.query(
        #     Module.code
        # ).join(
        #     ModuleEnrolment,
        #     ModuleEnrolment.module_code == Module.code
        # ).all()
        module_codes = db.session.query(
            Module.code
        ).join(
            ModuleEnrolment,
            ModuleEnrolment.module_code == Module.code
        ).filter(
            ModuleEnrolment.account_id == self.id
        ).all()
        # x[0] represents the first (and only) column in each tuple in the list of results (this is the 'code' column)
        return [x[0] for x in module_codes]

    def get_available_questions(self):
        if self.role == 'student':
            print('ERROR: Something has gone wrong. Student account shouldn\'t be calling get_available_questions()')
            return None
        module_codes = self.get_enrolled_module_codes()
        print(f'codes {module_codes}')
        # reference 14 April https://stackoverflow.com/questions/887388/is-there-support-for-the-in-operator-in-the-sql-expression-language-used-in-sq/887402#887402
        return db.session.query(
            Question
        ).filter(
            Question.module_code.in_(
                module_codes
            )
        )

    def get_available_assessments_lecturer(self):
        module_codes = self.get_enrolled_module_codes()
        # reference 14 April https://stackoverflow.com/questions/887388/is-there-support-for-the-in-operator-in-the-sql-expression-language-used-in-sq/887402#887402
        return db.session.query(
            Assessment
        ).filter(
            Assessment.module.in_(
                module_codes
            )
        ).all()

    def update_credit(self, id, credit):
        result = self.search_account_by_id(id)
        result.credit = int(result.credit) + credit if result.credit else credit
        db.session.commit()

    @staticmethod
    def get_current_user():
        return current_user.id


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(AccountModel).get(int(user_id))
