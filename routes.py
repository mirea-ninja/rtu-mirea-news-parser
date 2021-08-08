import requests
from main import app, config, logging
from database import NewsDB, Image, Session, get_db
from typing import Optional
from news_parse import News
from models import NewsModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse, FileResponse
from typing import List
from fastapi import Depends
from request_setting import Request


@app.get("/news", response_model=List[NewsModel], tags=["news"])
def get_news(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """Выводим новости.
       Сортировка по дате. (desc)
    """
    results = db.query(NewsDB).order_by(NewsDB.date.desc()
                                        ).offset(offset).limit(limit).all()
    list_models = [NewsModel.from_orm(model) for model in results]
    for model in list_models:
        for image in model.images:
            image.name = config['project']['host'] + "/photo/" + image.name

    return list_models


@app.get("/news/count", response_model=int, tags=["news"])
def get_news(db: Session = Depends(get_db)):
    """Количество новостей
    """
    return ORJSONResponse(content=db.query(NewsDB).count())


@app.get("/news/start", tags=["news"])
def start_news_parsing(db: Session = Depends(get_db),
                       http_session: requests.Session = Depends(Request.start_session)):
    """Старт парсинг новостей"""
    news = News(db=db, http_session=http_session)
    news.start_parsing()
    return ORJSONResponse(content="Success")


@app.get("/photo/{image}", tags=["image"])
def get_photo(image: str, db: Session = Depends(get_db),
              http_session: requests.Session = Depends(Request.start_session)):
    return FileResponse(config['database']['media_folder']+"/"+image, media_type="image/png")
