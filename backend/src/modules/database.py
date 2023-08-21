"""
Database connection settings for sessions
"""
# pylint: disable=line-too-long, invalid-name, inconsistent-return-statements
import base64
import json
import os
import timeout_decorator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.modules.common import RequestException
from src.modules.auto_models import ChatgptLog


class postgresql_db:
    """
    Database connection class
    """
    POSTGRES_DATABASE_URL = os.environ["DATABASE_URL"]
    def db_login(self):
        """
        Logs user into the DB using a secret
        """
        try:
            return self.POSTGRES_DATABASE_URL
        except ClientError as e:
            print(e.response["Error"]["Code"])
            raise e

    def __init__(self):
        self.engine = create_engine(self.POSTGRES_DATABASE_URL)

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )


db = postgresql_db()
    
def get_db_engine():
    db_engine = db.engine
    return db_engine

def get_db():
    """
    Creates a Database connection for sessions
    """
    db_engine = db.SessionLocal()
    try:
        yield db_engine
    finally:
        db_engine.close()



@timeout_decorator.timeout(3)
def uuid_exists(uuid_to_check, session):
    """
    Checks if a given UUID already exists in the database.
    Returns:
    True if UUID exists, False otherwise.
    """
    try:
        # attempt to retrieve a record with the given UUID
        result = session.query(ChatgptLog).filter_by(id=str(uuid_to_check)).first()
        return bool(result)
    except timeout_decorator.TimeoutError as error:
        # Rethrow the TimeoutError as a RequestException, with your custom message.
        raise RequestException(
            status_code=504,
            msg="The operation timed out. Please try again later.",
        ) from error
    except Exception as error:
        raise RequestException(
            status_code=500,
            msg=f"Unknown error: {error}",
        ) from error
