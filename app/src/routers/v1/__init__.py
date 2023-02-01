from fastapi import APIRouter

from routers.v1 import login, signup, verify, category, article

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(login.router)
v1_router.include_router(signup.router)
v1_router.include_router(verify.router)
v1_router.include_router(category.router)
v1_router.include_router(article.router)
