"""Работа со Strapi"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from app import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, ForeignKey
from fastapi import Depends

engine = create_engine(config['database']['url'], connect_args={
                       "check_same_thread": False})
Session = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


class NewsDB(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    text = Column(String(1024))
    date = Column(Date)
    images = relationship("Image", lazy='joined', backref="news")


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    news_id = Column(Integer, ForeignKey('news.id'))


# Создаём таблицы.
Base.metadata.create_all(engine)
