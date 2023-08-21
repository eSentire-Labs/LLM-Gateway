"""
The code in this repo is designed to create docker postgres db to get you started immediately.
But as this database could contain very sensitive information,
eSentire Labs recommends you replace the docker container database with a production level database of your own.
"""
import os

from sqlalchemy import create_engine, DDL
from sqlalchemy.orm import sessionmaker
from src.modules.auto_models import Base


engine = create_engine(os.environ["DATABASE_URL"])

install_ext_statement = DDL('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
create_schema_statement = DDL('CREATE SCHEMA IF NOT EXISTS llm_logs')

with engine.begin() as connection:
    connection.execute(create_schema_statement)
    connection.execute(install_ext_statement)

Base.metadata.create_all(engine)