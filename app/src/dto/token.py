from pydantic import BaseModel


class TokenDTO(BaseModel):
    expire_at: int
    token: str


class TokensDTO(BaseModel):
    access_token: TokenDTO
