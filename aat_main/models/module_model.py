from sqlalchemy import MetaData, Table

from aat_main import db
from aat_main.models.enrolment_models import ModuleEnrolment


class Module(db.Model):
    __tablename__ = 'module'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    code: varchar(8), primary
    name: varchar(128)
    """

    @staticmethod
    def get_all():
        return db.session.query(Module).all()

    @staticmethod
    def get_module_by_id(id):
        return db.session.query(Module).get(id)

    @staticmethod
    def create_module(code, name):
        db.session.add(Module(code=code, name=name))
        db.session.commit()

    def get_enrolled_all(self):
        # This import is inside the function to avoid a circular import (since account_model.py tries to import this
        # file)
        from aat_main.models.account_model import AccountModel

        return db.session.query(
            AccountModel
        ).join(
            ModuleEnrolment,
            ModuleEnrolment.account_id == AccountModel.id,
        ).filter(
            ModuleEnrolment.module_code == self.code
        ).all()

    def get_enrolled_students(self):
        all_enrolled_accounts = self.get_enrolled_all()
        return [account for account in all_enrolled_accounts if account.role == 'student']

    def get_enrolled_staff(self):
        all_enrolled_accounts = self.get_enrolled_all()
        return [account for account in all_enrolled_accounts if account.role == 'staff']
