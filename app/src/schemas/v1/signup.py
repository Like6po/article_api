from pydantic import EmailStr, validator
from pydantic.main import BaseModel


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    password_repeat: str

    @validator('password')
    def check_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value

    @validator('password_repeat')
    def check_password_repeat(cls, value: str, values: dict):
        password = values.get('password')
        if value != password:
            raise ValueError("Passwords do not match")
        return value


class SignUpResponse(BaseModel):
    message: str
