from pydantic import BaseModel


class UserShortResponse(BaseModel):
    id: int
    email: str
