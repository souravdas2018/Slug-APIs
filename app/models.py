"""
Defines the database schema for the URL shortener service, including
columns for original URL, shortened URL, and creation timestamp.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class USER(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'url_shortener'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with URLs
    urls = relationship("URL", back_populates="owner")


class URL(Base):
    __tablename__ = "all_urls"
    __table_args__ = {'schema': 'url_shortener'}

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    slug_url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Foreign key to associate URL with USER
    owner_id = Column(Integer, ForeignKey('url_shortener.users.id'))
    owner = relationship("USER", back_populates="urls")

class URL_TRACKING(Base):
    __tablename__ = "url_tracking"
    __table_args__ = {'schema': 'url_shortener'}

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey('url_shortener.all_urls.id'))
    access_time = Column(DateTime, default=datetime.utcnow)