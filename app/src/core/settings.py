from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv('.env')


class JWT(BaseSettings):
    SECRET_KEY: str = '123'

    class Config:
        env_prefix = 'JWT_'


class Postgres(BaseSettings):
    USER: str = "user"
    PASSWORD: str = "123"
    DB: str = "db"
    HOST: str = "localhost"
    PORT: str = "5432"

    class Config:
        env_prefix = 'POSTGRES_'

    def build_url(self) -> str:
        return f'postgresql+asyncpg://' \
               f'{self.USER}:{self.PASSWORD}@' \
               f'{self.HOST}:{self.PORT}/{self.DB}'


class Redis(BaseSettings):
    HOST: str = "localhost"
    PORT: str = "6379"

    class Config:
        env_prefix = 'REDIS_'

    def build_url(self) -> str:
        return f'redis://{self.HOST}:{self.PORT}'


class SMTP(BaseSettings):
    HOST: str = "smtp.gmail.com"
    PORT: int = 587
    EMAIL: str
    PASSWORD: str

    class Config:
        env_prefix = 'SMTP_'


class Settings(BaseSettings):
    DEBUG: bool = True
    POSTGRES: Postgres = Postgres()
    REDIS: Redis = Redis()
    JWT: JWT = JWT()
    SMTP: SMTP = SMTP()


SETTINGS = Settings()
