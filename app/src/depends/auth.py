from jose import JWSError, JWTError

from core.jwt import JWTRepository, TokenPayloadDTO, JWTTypeError
from depends.db import get_user_service
from depends.jwt import get_jwt_repository
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from starlette import status

from models import UserModel
from services.database.user import UserService

oauth2_scheme = HTTPBearer()


async def get_token_payload(
        token=Depends(oauth2_scheme),
        jwt_repository: JWTRepository = Depends(get_jwt_repository),
):
    try:
        payload = jwt_repository.access.get_payload(token.credentials)
    except (JWTError, JWSError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )
    except JWTTypeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type",
        )
    if payload:
        return payload
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid token",
    )


async def get_user_from_jwt(
        payload: TokenPayloadDTO = Depends(get_token_payload),
        users_service: UserService = Depends(get_user_service),
) -> UserModel:
    user: UserModel | None = await users_service.get_by_id(id=int(payload.sub))
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid token",
    )
