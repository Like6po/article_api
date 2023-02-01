import datetime

from pydantic.main import BaseModel


class ShortCategoryResponse(BaseModel):
    id: int
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: datetime.datetime
    edited_at: datetime.datetime | None


class CategoryCreateRequest(BaseModel):
    name: str


class CategoryCreateResponse(BaseModel):
    id: int


class CategoryPatchRequest(BaseModel):
    name: str
