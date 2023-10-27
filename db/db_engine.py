import os
from typing import Union

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from bot_app.registration import Student
from logs.logger import get_logger

logger = get_logger(
    logger_name='postgres',
    log_file_name='logs/database.log'
)
load_dotenv()
DATABASE_URL = (f'postgresql://{os.getenv("POSTGRES_USER_NAME")}:{os.getenv("POSTGRES_USER_PASSWORD")}'
                f'@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("DATABASE_NAME")}')

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User:
    def __init__(self, user_id: Union[int, str]):
        self.user_id = user_id

    def add_user(self, username: str):
        """Adding a user to the database

        :param username: Username
        :type username: str
        """
        try:
            session = Session()
            with session:
                new_user = Results(
                    user_id=self.user_id, username=username
                )
                session.add(new_user)
                session.commit()
        except Exception as ex:
            logger.error(ex)

    def add_user_info(self, student: Student):
        """Adding general student information

        :param student: Student object
        :return:
        """
        try:
            session = Session()

            with session:
                user = session.query(Results).filter_by(user_id=self.user_id).first()

                user.first_name = student.student_name
                user.last_name = student.student_last_name
                user.student_class = student.student_class

                session.commit()
        except Exception as ex:
            logger.error(ex)

    def edit_factor(self, factor: str, value: Union[int, str]):
        """Adding Factor Points

        :param factor: edited factor family_factor / psychological_factor / env_factor / school_factor
        :param value: added value
        :return:
        """
        try:
            session = Session()
            with session:
                user = session.query(Results).filter_by(user_id=self.user_id).first()
                new_factor = getattr(user, factor) + int(value)
                setattr(user, factor, new_factor)
                session.commit()
        except Exception as ex:
            logger.error(ex)

    def set_results(self):
        """Calculate and update result values for a user.

        :param user_id: User ID
        :type user_id: int | str
        """
        try:
            session = Session()
            with session:
                user = session.query(Results).filter_by(user_id=self.user_id).first()

                user.total_risk = (
                        user.family_factor +
                        user.psychological_factor +
                        user.env_factor +
                        user.school_factor
                )

                if user.age_category == '14-15 лет':
                    factors = {
                        'family_factor': {
                            (0, 15): 'Низкая',
                            (16, 26): 'Средняя',
                            (27, 100): 'Высокая',
                        },
                        'psychological_factor': {
                            (0, 20): 'Низкая',
                            (21, 37): 'Средняя',
                            (38, 100): 'Высокая',
                        },
                        'env_factor': {
                            (0, 24): 'Низкая',
                            (25, 41): 'Средняя',
                            (42, 100): 'Высокая',
                        },
                        'school_factor': {
                            (0, 9): 'Низкая',
                            (10, 14): 'Средняя',
                            (15, 100): 'Высокая',
                        },
                        'total_risk': {
                            (0, 68): 'Низкая',
                            (69, 118): 'Средняя',
                            (119, 200): 'Высокая',
                        },
                    }
                else:
                    factors = {
                        'family_factor': {
                            (0, 17): 'Низкая',
                            (18, 33): 'Средняя',
                            (34, 100): 'Высокая',
                        },
                        'psychological_factor': {
                            (0, 16): 'Низкая',
                            (17, 37): 'Средняя',
                            (38, 100): 'Высокая',
                        },
                        'env_factor': {
                            (0, 22): 'Низкая',
                            (23, 42): 'Средняя',
                            (43, 100): 'Высокая',
                        },
                        'school_factor': {
                            (0, 10): 'Низкая',
                            (11, 16): 'Средняя',
                            (17, 100): 'Высокая',
                        },
                        'total_risk': {
                            (0, 65): 'Низкая',
                            (66, 128): 'Средняя',
                            (129, 200): 'Высокая',
                        },
                    }
                for factor, results in factors.items():
                    for (low, high), result in results.items():
                        if low <= getattr(user, factor) <= high:
                            setattr(user, factor + '_result', result)
                            break

                session.commit()
        except Exception as ex:
            logger.error(ex)

    def add_bug_report(self, description: str):
        """Add a bug report to the database.

        :param description: Bug report text
        :type description: str
        """
        try:
            session = Session()
            with session:
                bug_report = BugReport(
                    user_id=self.user_id,
                    description=description
                )
                session.add(bug_report)
                session.commit()
        except Exception as ex:
            logger.error(ex)

    def edit_bug_report_status(self, status: str):
        """Edit the status of a bug report in the database.

        :param status: Bug report status
        :type status: str
        """
        try:
            session = Session()
            with session:
                bug_report = session.query(BugReport).filter_by(user_id=self.user_id).first()

                if bug_report:
                    bug_report.report_status = status
                    session.commit()
        except Exception as ex:
            logger.error(ex)


def add_user(user_id: Union[int, str], username: str):
    """Добавление пользователя в базу данных

    :param user_id: User ID
    :type user_id: int | str
    :param username: Username
    :type username: str
    """
    try:
        session = Session()
        with session:
            new_user = Results(
                user_id=user_id, username=username
            )
            session.add(new_user)
            session.commit()
    except Exception as ex:
        logger.error(ex)


class Results(Base):
    __tablename__ = 'results'

    # Telegram data
    user_id = Column(Integer, primary_key=True)
    username = Column(String)

    # User input data
    first_name = Column(String, nullable=True, default=None)
    last_name = Column(String, nullable=True, default=None)
    student_class = Column(String, nullable=True, default=None)
    age_category = Column(String, nullable=True, default=None)

    # Total results data
    family_factor = Column(Integer, nullable=False, default=0)
    psychological_factor = Column(Integer, nullable=False, default=0)
    env_factor = Column(Integer, nullable=False, default=0)
    school_factor = Column(Integer, nullable=False, default=0)
    total_risk = Column(Integer, nullable=False, default=0)

    # Total results data in the string format
    family_factor_result = Column(String, nullable=True)
    psychological_factor_result = Column(String, nullable=True)
    env_factor_result = Column(String, nullable=True)
    school_factor_result = Column(String, nullable=True)
    total_risk_result = Column(String, nullable=True)

    bug_reports = relationship('BugReport', back_populates='user', cascade='all, delete-orphan')


class BugReport(Base):
    __tablename__ = 'bug_reports'

    report_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('results.user_id'))
    report_status = Column(String, nullable=False, default='Open')
    description = Column(String, nullable=False)

    # Define a relationship between BugReports and Results tables
    user = relationship('Results', back_populates='bug_reports')


Base.metadata.create_all(engine)
