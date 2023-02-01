from fastapi import APIRouter

from routers import health
from .v1 import v1_router

root_router = APIRouter(prefix="/api")

root_router.include_router(v1_router)
root_router.include_router(health.router)
