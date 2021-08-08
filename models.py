from typing import List
from pydantic import BaseModel
from datetime import date
from typing import List, Optional


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

    class Config:
        orm_mode = True
