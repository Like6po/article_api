from core.settings import SETTINGS
from core.jwt import JWTRepository

jwt_repository = JWTRepository(
    secret_key=SETTINGS.JWT.SECRET_KEY
)


def get_jwt_repository() -> JWTRepository:
    return jwt_repository
