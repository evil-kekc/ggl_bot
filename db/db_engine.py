import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = (f'postgresql://{os.getenv("POSTGRES_USER_NAME")}:{os.getenv("POSTGRES_USER_PASSWORD")}'
                f'@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("DATABASE_NAME")}')

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


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


Base.metadata.create_all(engine)
