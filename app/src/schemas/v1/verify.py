from pydantic import validator, EmailStr
from pydantic.main import BaseModel


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str

    @validator("code")
    def check_code(cls, value: int):
        if len(str(value)) != 6:
            raise ValueError("Code must be 6 characters long")
        return value


class VerifyResponse(BaseModel):
    message: str
