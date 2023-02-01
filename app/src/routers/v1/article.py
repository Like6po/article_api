from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status

from depends.auth import get_user_from_jwt
from depends.db import get_article_service, get_category_service
from models import ArticleModel, UserModel
from schemas.v1.article import ShortArticleResponse, ArticleResponse, ArticleCreateResponse, ArticleCreateRequest
from schemas.v1.category import ShortCategoryResponse
from schemas.v1.user import UserShortResponse
from services.database.article import ArticleService
from services.database.category import CategoryService

router = APIRouter()


@router.get(
    path='/articles',
    status_code=status.HTTP_200_OK,
    response_model=list[ShortArticleResponse]
)
async def get_articles(
        category_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        article_service: ArticleService = Depends(get_article_service)
):
    return [ShortArticleResponse(id=article.id,
                                 title=article.title,
                                 categories=
                                 [ShortCategoryResponse(id=category.id,
                                                        name=category.name)
                                  for category in article.categories])
            for article in
            await article_service.get_list(category_id=category_id,
                                           limit=limit,
                                           offset=offset)]


@router.get(
    path="/articles/{article_id}",
    status_code=status.HTTP_200_OK,
    response_model=ArticleResponse
)
async def get_article(
        article_id: int,
        article_service: ArticleService = Depends(get_article_service)
):
    article: ArticleModel | None = await article_service.get_extended_by_id(id=article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Article not found")
    return ArticleResponse(id=article.id,
                           created_at=article.created_at,
                           edited_at=article.edited_at,
                           title=article.title,
                           text=article.text,
                           user=UserShortResponse(
                               id=article.user.id,
                               email=article.user.email,
                           ),
                           categories=[ShortCategoryResponse(
                               id=category.id,
                               name=category.name,
                           ) for category in article.categories])


@router.delete(
    path="/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_article(
        article_id: int,
        user: UserModel = Depends(get_user_from_jwt),
        article_service: ArticleService = Depends(get_article_service)
):
    article: ArticleModel | None = await article_service.get_extended_by_id(id=article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Article not found")
    if article.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied")
    await article_service.delete_by_id(article_id)


@router.post(
    path="/articles",
    status_code=status.HTTP_200_OK,
    response_model=ArticleCreateResponse
)
async def post_article(
        data: ArticleCreateRequest,
        user: UserModel = Depends(get_user_from_jwt),
        article_service: ArticleService = Depends(get_article_service),
        category_service: CategoryService = Depends(get_category_service)
):
    if not (await category_service.exists_list(data.categories)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="One from categories not found")

    article: ArticleModel = await article_service.add(title=data.title,
                                                      text=data.text,
                                                      user_id=user.id,
                                                      categories=data.categories)

    return ArticleCreateResponse(id=article.id)


@router.patch(
    path="/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def patch_article(
        article_id: int,
        data: ArticleCreateRequest,
        user: UserModel = Depends(get_user_from_jwt),
        article_service: ArticleService = Depends(get_article_service),
        category_service: CategoryService = Depends(get_category_service)
):
    article: ArticleModel | None = await article_service.get_extended_by_id(id=article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Article not found")
    if article.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied")

    if not (await category_service.exists_list(data.categories)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="One from categories not found")

    await article_service.update(id=article_id,
                                 title=data.title,
                                 text=data.text,
                                 user_id=user.id,
                                 categories=data.categories)
