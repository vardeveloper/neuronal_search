import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(
    "postgresql://{}:{}@{}:{}/{}".format(
        os.getenv("DB_USER"),
        os.getenv("DB_PASS"),
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_NAME"),
    ),
    echo=bool(os.getenv("DEBUG"))
)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
