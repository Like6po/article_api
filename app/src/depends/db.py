from fastapi import Depends

from depends.session import get_session
from services.database.article import ArticleService
from services.database.category import CategoryService
from services.database.user import UserService


def get_user_service(session=Depends(get_session)) -> UserService:
    return UserService(session_or_pool=session)


def get_category_service(session=Depends(get_session)) -> CategoryService:
    return CategoryService(session_or_pool=session)


def get_article_service(session=Depends(get_session)) -> ArticleService:
    return ArticleService(session_or_pool=session)
