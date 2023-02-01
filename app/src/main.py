from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import SETTINGS
from depends import session
from fixtures import load_fixtures
from models import *
from routers import root_router

app = FastAPI(
    title="Article API",
    docs_url='/api/docs',
    openapi_url='/api/openapi.json',
)
app.include_router(root_router)


@app.on_event('startup')
async def startup():
    engine = create_async_engine(
        SETTINGS.POSTGRES.build_url(),
        connect_args={
            'server_settings':
                {
                    'application_name': "article_api"
                }
        },
    )
    session.session_factory = sessionmaker(bind=engine,
                                           expire_on_commit=False,
                                           class_=AsyncSession)

    if SETTINGS.DEBUG:
        async with engine.begin() as conn:
            await conn.run_sync(DatabaseModel.metadata.drop_all)
            await conn.run_sync(DatabaseModel.metadata.create_all)

        await load_fixtures(session.session_factory)
