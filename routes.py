import requests
from main import app, config
from database import NewsDB, Session, Tag, get_db, secondary_tag
import news_parse
import auth
from models import NewsModel, News, TagModel, TagsModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse, FileResponse
from fastapi import Depends, HTTPException, status
from request_setting import Request

from fastapi.security import APIKeyHeader

oauth2_scheme = APIKeyHeader(name="api-key")


@app.get("/news", response_model=News, tags=["news"])
def get_news(tag: str = 'все', limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """Выводим новости.
       Сортировка по дате. (desc)
    """
    filter_tag = None == None if tag == 'все' else Tag.name == tag
    results = db.query(NewsDB).filter(filter_tag).order_by(
        NewsDB.date.desc()).limit(limit).offset(offset).all()

    list_models = [NewsModel.from_orm(model) for model in results]
    for model in list_models:
        for image in model.images:
            image.name = config['project']['host'] + "/photo/" + image.name

    return jsonable_encoder(obj={"news": list_models})


@app.get("/news/count", response_model=int, tags=["news"])
def get_news(db: Session = Depends(get_db)):
    """Количество новостей
    """
    return ORJSONResponse(content=db.query(NewsDB).count())


@app.get("/news/start", tags=["news"])
def start_news_parsing(db: Session = Depends(get_db), token=Depends(oauth2_scheme) if auth.check_environ() == True else None,
                       http_session: requests.Session = Depends(Request.start_session)):
    """Старт парсинг новостей"""
    if auth.access_api_key(token):
        news = news_parse.News(db=db, http_session=http_session)
        news.start_parsing()
        return ORJSONResponse(content="Success")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect api-key",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/photo/{image}", tags=["image"])
def get_photo(image: str):
    return FileResponse(config['database']['media_folder'] + "/" + image, media_type="image/png")


@app.get("/tags", tags=['tags'], response_model=TagsModel)
def get_tags(db: Session = Depends(get_db)):
    results = db.query(Tag).all()
    return jsonable_encoder(obj={"tags": [TagModel.from_orm(tag) for tag in results]})
