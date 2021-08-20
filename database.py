"""Работа со Strapi"""
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from main import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Table

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


secondary_tag = Table('tags_news', Base.metadata,
                      Column('news_id', ForeignKey('news.id')),
                      Column('tag_id', ForeignKey('tag.id'))
                      )


class NewsDB(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    text = Column(String(1024))
    date = Column(Date)
    images = relationship("Image", lazy='joined', backref="news")
    tags = relationship("Tag",
                        secondary=secondary_tag, lazy='joined')


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    news_id = Column(Integer, ForeignKey('news.id'))


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    name = Column(String(32))

    @staticmethod
    def search(tags_names: Optional[list[String]], db):
        """Получаем теги, но не создаём. Нужно подтвердить, если получили созданные теги"""
        tags = db.query(Tag).filter(Tag.name.in_(tags_names)).all()
        tags_name_found = [tag.name for tag in tags]
        tags_none_found = [
            tag for tag in tags_names if tag not in tags_name_found]
        if len(tags_none_found) > 0:
            tags.extend([Tag(name=tag) for tag in tags_none_found])
        return tags


# Создаём таблицы.
Base.metadata.create_all(engine)
