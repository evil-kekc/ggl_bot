import os
from typing import Union

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = (f'postgresql://{os.getenv("POSTGRES_USER_NAME")}:{os.getenv("POSTGRES_USER_PASSWORD")}'
                f'@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("DATABASE_NAME")}')

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def set_results(user_id: Union[int, str]):
    """Calculate and update result values for a user.

    :param user_id: User ID
    :type user_id: int | str
    """
    session = Session()
    user = session.query(Results).filter_by(user_id=user_id).first()

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


Base.metadata.create_all(engine)
