from typing import List
from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class TagModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TagsModel(BaseModel):
    tags: List[TagModel]


class ImageModel(BaseModel):
    name: str

    class Config:
        orm_mode = True


class NewsModel(BaseModel):
    id: int
    title: str
    text: str
    date: date
    images: List[ImageModel]
    tags: List[TagModel]

    class Config:
        orm_mode = True


class News(BaseModel):
    news: List[NewsModel]
