from pydantic import EmailStr, validator
from pydantic.main import BaseModel

from dto.token import TokenDTO


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def check_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class LoginResponse(BaseModel):
    id: str
    access_token: TokenDTO
