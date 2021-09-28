import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
    os.getenv('DB_USER', 'postgres'),
    os.getenv('DB_PASS', 'postgres'),
    os.getenv('DB_HOST', 'localhost'),
    os.getenv('DB_PORT', 5432),
    os.getenv('DB_NAME', 'jina_search')
))

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
