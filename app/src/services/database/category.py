from models import CategoryModel
from services.database.base import DatabaseService


class CategoryService(DatabaseService):
    model = CategoryModel

    async def get_list(self, limit: int | None = None, offset: int | None = None):
        return await self._get_all(limit=limit if limit else 50,
                                   offset=offset if offset else 0)

    async def exists_list(self, ids: list[int]):
        if not ids:
            return True
        categories = await self._get_all(CategoryModel.id.in_(ids))  # noqa:ignore
        return len(categories) == len(ids)

    async def get_by_id(self, id: int) -> CategoryModel:
        return await self._get_one(CategoryModel.id == id)

    async def add(self, **kwargs) -> CategoryModel:
        return await self._add(**kwargs)

    async def delete_by_id(self, id: int) -> None:
        await self._delete(CategoryModel.id == id)

    async def update_by_id(self, id: int, **kwargs):
        await self._update(CategoryModel.id == id, **kwargs)
