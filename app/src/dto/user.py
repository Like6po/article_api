from pydantic import BaseModel

from dto.token import TokenDTO


class LoginDTO(BaseModel):
    sub: int
    access_token: TokenDTO
