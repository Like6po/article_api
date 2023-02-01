from typing import cast

from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload

from models import ArticleModel, CategoryToArticle
from services.database.base import DatabaseService, make_proxy_bulk_save_func


class ArticleService(DatabaseService):
    model = ArticleModel

    async def get_list(self, category_id: int | None = None,
                       limit: int | None = None,
                       offset: int | None = None):

        statement = select(self.model)
        if category_id:
            statement = statement.join(CategoryToArticle,
                                       CategoryToArticle.article_id == ArticleModel.id). \
                where(CategoryToArticle.category_id == category_id)
        statement = statement.limit(limit if limit else 50)
        statement = statement.offset(offset if offset else 0)
        statement = statement.options(joinedload(ArticleModel.categories))

        async with self._transaction:
            scalars = (await self._session.execute(statement)).scalars().unique().all()
        return cast(list[ArticleModel], scalars)

    async def get_by_id(self, id: int) -> ArticleModel:
        return await self._get_one(ArticleModel.id == id)

    async def get_extended_by_id(self, id: int) -> ArticleModel:
        return await self._get_one(ArticleModel.id == id,
                                   loads=[ArticleModel.categories,
                                          ArticleModel.user])

    async def add(self, user_id: int, categories: list[int],
                  **kwargs) -> ArticleModel:
        async with self._transaction:
            article = self.model(user_id=user_id, **kwargs)
            self._session.add(article)
            await self._session.flush()
            categories_to_article = [CategoryToArticle(category_id=category_id,
                                                       article_id=article.id)
                                     for category_id in categories]
            bulk_save_func = make_proxy_bulk_save_func(instances=categories_to_article)
            await self._session.run_sync(bulk_save_func)
        return article

    async def update(self, id, categories: list[int],
                     **kwargs):
        async with self._transaction:
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            await self._session.execute(update(self.model).where(ArticleModel.id == id).
                                        values(**kwargs))
            if categories:
                await self._session.execute(delete(CategoryToArticle).
                                            where(CategoryToArticle.article_id == id))
                categories_to_article = [CategoryToArticle(category_id=category_id,
                                                           article_id=id)
                                         for category_id in categories]
                bulk_save_func = make_proxy_bulk_save_func(instances=categories_to_article)
                await self._session.run_sync(bulk_save_func)

    async def delete_by_id(self, id: int) -> None:
        await self._delete(ArticleModel.id == id)

    async def update_by_id(self, id: int, **kwargs):
        await self._update(ArticleModel.id == id, **kwargs)
