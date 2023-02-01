from fastapi import APIRouter, status, Depends, HTTPException

from core.jwt import JWTRepository
from depends.jwt import get_jwt_repository
from dto.token import TokenDTO
from dto.user import LoginDTO
from schemas.v1.login import LoginResponse, LoginRequest
from services.database.user import UserService, UserNotExistsError, UserBadPasswordError, UserNotVerifiedError
from depends.db import get_user_service

router = APIRouter()


@router.post(
    path='/login',
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse
)
async def login(
        data: LoginRequest,
        jwt_repository: JWTRepository = Depends(get_jwt_repository),
        user_service: UserService = Depends(get_user_service)
):
    try:
        auth_data: LoginDTO = await user_service.login(
            jwt_repository=jwt_repository,
            email=data.email,
            password=data.password)
    except (UserNotExistsError, UserBadPasswordError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Bad credentials")
    except UserNotVerifiedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User not verified")
    return LoginResponse(id=auth_data.sub,
                         access_token=TokenDTO(
                             **auth_data.access_token.dict()
                         ))
