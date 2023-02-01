from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from depends.auth import get_user_from_jwt
from depends.db import get_category_service
from models import CategoryModel, UserModel
from schemas.v1.category import ShortCategoryResponse, CategoryResponse, CategoryCreateRequest, CategoryCreateResponse, \
    CategoryPatchRequest
from services.database.category import CategoryService

router = APIRouter()


@router.get(
    path='/categories',
    status_code=status.HTTP_200_OK,
    response_model=list[ShortCategoryResponse]
)
async def get_categories(
        limit: int | None = None,
        offset: int | None = None,
        category_service: CategoryService = Depends(get_category_service)
):
    return [ShortCategoryResponse(**category.as_dict())
            for category in
            await category_service.get_list(limit=limit,
                                            offset=offset)]


@router.get(
    path="/categories/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryResponse
)
async def get_category(
        category_id: int,
        category_service: CategoryService = Depends(get_category_service)
):
    category: CategoryModel | None = await category_service.get_by_id(id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found")
    return CategoryResponse(**category.as_dict())


@router.post(
    path="/categories",
    status_code=status.HTTP_200_OK,
    response_model=CategoryCreateResponse
)
async def post_category(
        data: CategoryCreateRequest,
        user: UserModel = Depends(get_user_from_jwt),
        category_service: CategoryService = Depends(get_category_service),
):
    category: CategoryModel = await category_service.add(name=data.name,
                                                         user_id=user.id)
    return CategoryCreateResponse(id=category.id)


@router.delete(
    path="/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
        category_id: int,
        user: UserModel = Depends(get_user_from_jwt),
        category_service: CategoryService = Depends(get_category_service),
):
    category: CategoryModel | None = await category_service.get_by_id(id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found")
    if category.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Access denied")
    await category_service.delete_by_id(id=category_id)


@router.patch(
    path="/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def patch_category(
        category_id: int,
        data: CategoryPatchRequest,
        user: UserModel = Depends(get_user_from_jwt),
        category_service: CategoryService = Depends(get_category_service),
):
    category: CategoryModel | None = await category_service.get_by_id(id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found")
    if category.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Access denied")
    await category_service.update_by_id(id=category_id, **data.dict())
