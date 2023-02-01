from fastapi import APIRouter, status, Depends, HTTPException

from depends.db import get_user_service
from depends.redis import get_redis_service
from models import UserModel
from schemas.v1.signup import SignUpRequest
from schemas.v1.verify import VerifyResponse, VerifyRequest
from services.database.user import UserService
from services.redis import RedisService

router = APIRouter()


@router.post(
    path='/verify',
    status_code=status.HTTP_200_OK,
    response_model=VerifyResponse
)
async def verify(
        data: VerifyRequest,
        user_service: UserService = Depends(get_user_service),
        redis_service: RedisService = Depends(get_redis_service),
):
    user: UserModel | None = await user_service.get_by_email(email=data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Account not found")
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already verified")
    code = await redis_service.get(data.email)
    if not code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Code not found")
    await redis_service.remove(data.email)
    await user_service.set_verified(email=data.email)
    return VerifyResponse(message="Ok")
