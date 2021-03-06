from uuid import uuid4
import datetime
from dateutil import tz

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean,
    Unicode,
    ForeignKey,
)

# from db import Base, engine
from db.base_class import Base
from db.session import engine


time_zone = tz.gettz("America/Lima")
utc = datetime.datetime.now(tz=time_zone)
now = utc.strftime("%Y-%m-%d %H:%M:%S")

def _uuid4():
    return str(uuid4())


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(
        Unicode(36), ForeignKey("log.uuid", ondelete="CASCADE"), nullable=False
    )
    qualification = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=now)

    def __init__(self, uuid, qualification):
        self.uuid = uuid
        self.qualification = qualification

    def __repr__(self):
        return f"Feedback({self.uuid}, {self.qualification})"

    def __str__(self):
        return self.uuid


class Log(Base):
    __tablename__ = "log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(Unicode(36), nullable=False, index=True, unique=True, default=_uuid4)
    search = Column(Text, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    business = Column(String, nullable=False)
    category = Column(String, nullable=False)
    flow_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=now)

    def __init__(
        self, uuid, search, question, answer, business, category, flow_id, session_id
    ):
        self.uuid = uuid
        self.search = search
        self.question = question
        self.answer = answer
        self.business = business
        self.category = category
        self.flow_id = flow_id
        self.session_id = session_id

    def __repr__(self):
        return f"Log({self.question}, {self.answer}, {self.business}, {self.category})"

    def __str__(self):
        return self.uuid


class QuestionAnswer(Base):
    __tablename__ = "question_answer"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(Unicode(36), nullable=False, index=True, unique=True, default=_uuid4)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    business = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=True)
    created_at = Column(DateTime, default=now)

    def __init__(self, question, answer, business, category, subcategory=None):
        self.question = question
        self.answer = answer
        self.business = business
        self.category = category
        self.subcategory = subcategory

    def __repr__(self):
        return f"QA({self.question}, {self.answer}, {self.business}, {self.category})"

    def __str__(self):
        return self.uuid


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)


class Customer(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    logo = Column(String)
    code = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean(), default=True)


class Dataset(Base):
    id = Column(Integer, primary_key=True, index=True)
    file = Column(String)
    customer_code = Column(String, unique=True, index=True, nullable=False)


def run():
    # feedback = Feedback('Python', 'Hello world', True)
    # db.session.add(feedback)
    # db.session.commit()
    # print(feedback.id)
    # print(feedback)
    pass


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    run()
