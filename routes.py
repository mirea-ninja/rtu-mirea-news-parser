import requests
from requests.api import request
from requests.sessions import session
from main import app, config, logging
from database import NewsDB, Image, Session, get_db
from typing import Optional
from news_parse import News
from models import NewsModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from fastapi import Depends
from request_setting import Request
import requests


@app.get("/news", response_model=List[NewsModel], tags=["news"])
def get_news(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """Выводим новости.
       Сортировка по дате. (desc)
    """
    return db.query(NewsDB).order_by(NewsDB.date.desc()).offset(offset).limit(limit).all()


@app.get("/news/count", response_model=int, tags=["news"])
def get_news(db: Session = Depends(get_db)):
    """Количество новостей
    """
    return JSONResponse(content=db.query(NewsDB).count())


@app.get("/news/start", tags=["news"])
def start_news_parsing(db: Session = Depends(get_db),
                       http_session: requests.Session = Depends(Request.start_session)):
    """Старт парсинг новостей"""
    news = News(db=db, http_session=http_session)
    news.start_parsing()
    return JSONResponse(content="Success")