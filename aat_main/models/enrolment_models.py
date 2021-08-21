from sqlalchemy import MetaData, Table

from aat_main import db


class ModuleEnrolment(db.Model):
    __tablename__ = 'module_enrolment'
    __table__ = Table(__tablename__, MetaData(bind=db.engine), autoload=True)
    """
    id: int, primary key, auto_increment
    account_id: int, foreign key
    module_code: varchar(8), foreign key
    """

    @staticmethod
    def get_all():
        return db.session.query(ModuleEnrolment).all()
