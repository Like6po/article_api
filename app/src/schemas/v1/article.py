import datetime

from pydantic import BaseModel, validator, root_validator

from schemas.v1.category import ShortCategoryResponse
from schemas.v1.user import UserShortResponse


class ShortArticleResponse(BaseModel):
    id: int
    title: str
    categories: list[ShortCategoryResponse]


class ArticleResponse(BaseModel):
    id: int
    created_at: datetime.datetime
    edited_at: datetime.datetime | None
    title: str
    text: str
    user: UserShortResponse
    categories: list[ShortCategoryResponse]


class ArticleCreateRequest(BaseModel):
    title: str | None = None
    text: str | None = None
    categories: list[int] | None = None

    @validator('categories')
    def check_categories(cls, value: list | None):
        if value and len(value) < 1:
            raise ValueError("Categories is empty")
        return value

    @root_validator(pre=True)
    def check_data_not_empty(cls, values: dict):
        if not values.values():
            raise ValueError("Empty data")
        return values


class ArticleCreateResponse(BaseModel):
    id: int
