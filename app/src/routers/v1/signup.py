from fastapi import APIRouter, status, Depends, HTTPException

from depends.db import get_user_service
from depends.email import get_email_service
from depends.redis import get_redis_service
from models import UserModel
from schemas.v1.signup import SignUpRequest, SignUpResponse
from services.database.user import UserService
from services.email import EmailService
from services.redis import RedisService

router = APIRouter()


@router.post(
    path='/signup',
    status_code=status.HTTP_200_OK,
    response_model=SignUpResponse
)
async def signup(
        data: SignUpRequest,
        user_service: UserService = Depends(get_user_service),
        redis_service: RedisService = Depends(get_redis_service),
        email_service: EmailService = Depends(get_email_service)
):
    user: UserModel | None = await user_service.get_by_email(email=data.email)
    if user and user.is_verified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already exists")
    code = await redis_service.get(data.email)
    if code:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    code = await email_service.send_code_to_email(data.email)
    await redis_service.set(key=data.email, value=code, expire=60)
    await user_service.signup(email=data.email, password=data.password)
    return SignUpResponse(message="Code sent")
