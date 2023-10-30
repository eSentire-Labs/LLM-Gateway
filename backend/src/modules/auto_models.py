"""
Use the classes to create objects when writing to the database or for creating the database
"""
# coding: utf-8
# pylint: disable=too-few-public-methods
from sqlalchemy import (
    Column,
    DateTime,
    Text,
    UniqueConstraint,
    text,
    Float,
    String,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

import base64
import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.modules.common import RequestException

Base = declarative_base()


class ChatgptLog(Base):
    """
    Auto Generated chatgpt logs class. This is the primary table with llm interactions are logged.
    """

    __tablename__ = "chatgpt_logs"
    __table_args__ = (UniqueConstraint("id", "user_name"), {"schema": "llm_logs"})

    id = Column(String, primary_key=True, default=str(UUID()))
    request = Column(Text)
    response = Column(Text)
    usage_info = Column(Text)
    user_name = Column(Text) # user metadata: username
    title = Column(Text) # user metadata: user job title
    response_time = Column(DateTime, server_default=text("now()"))
    convo_title = Column(String)
    convo_show = Column(Boolean, server_default=text("true"))
    root_gpt_id = Column(Text)

class MetaSummarizerLog(Base):
    """
    Auto Generated meta_summarizer_log logs class. This Table is used to garner metadata on prior chat interactions.
    """

    __tablename__ = "meta_summarizer_log"
    __table_args__ = (UniqueConstraint("id", "user_name"), {"schema": "llm_logs"})

    id = Column(String, primary_key=True, default=str(UUID()))
    request = Column(Text)
    response = Column(Text)
    usage_info = Column(Text)
    user_name = Column(Text)
    title = Column(Text)
    response_time = Column(DateTime, server_default=text("now()"))
    orig_summarized_id = Column(String)


class ImageLog(Base):
    """
    Auto Generated image gen logs class. This table captures interactions with the open ai image generation endpoint.
    """

    __tablename__ = "image_logs"
    __table_args__ = (UniqueConstraint("id", "user_name"), {"schema": "llm_logs"})

    id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    request = Column(Text)
    response = Column(Text)
    usage_cost = Column(Float)
    user_name = Column(Text)
    title = Column(Text)
    response_time = Column(DateTime, server_default=text("now()"))
