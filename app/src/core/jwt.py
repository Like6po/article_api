from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from jose import jwt, JWTError, JWSError
from pydantic.main import BaseModel
from pydantic.types import UUID4


class JWTTypeError(Exception):
    pass


class TokenPayloadDTO(BaseModel):
    exp: datetime
    sub: str
    iat: datetime
    type: str

    class Config:
        extra = 'allow'


class TokenDataDTO(BaseModel):
    token: str
    expire_at: int
    sub: str


class TokenTypes(Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class JWTTokenFactory:
    _type: Optional[TokenTypes] = None
    _algorithm: str = "HS256"

    def __init__(self,
                 secret_key: str,
                 lifetime_minutes: int):
        if not self._type:
            raise NotImplementedError
        self._secret_key: str = secret_key
        self._lifetime_minutes: int = lifetime_minutes
        self._payload: dict = {}

    def create(self, identifier: str) -> TokenDataDTO:
        self._payload = {}
        self._set_type()
        self._set_iat()
        self._set_exp()
        self._set_sub(identifier)
        token = jwt.encode(self._payload,
                           self._secret_key,
                           algorithm=self._algorithm)
        return TokenDataDTO(token=token,
                            expire_at=self._payload.get("exp"),
                            sub=identifier)

    def get_payload(self, token: str) -> TokenPayloadDTO:
        try:
            payload = jwt.decode(token,
                                 self._secret_key,
                                 algorithms=self._algorithm)
        except (JWTError, JWSError):
            raise
        if payload.get("type") != self._type:
            raise JWTTypeError(f"Type {payload.get('type')} "
                               "not supported")
        return TokenPayloadDTO(**payload)

    def _set_exp(self) -> None:
        self._payload["exp"] = (datetime.utcnow() +
                                timedelta(
                                    minutes=self._lifetime_minutes
                                )).timestamp()

    def _set_sub(self, sub: str | int | UUID4) -> None:
        self._payload["sub"] = str(sub)

    def _set_iat(self) -> None:
        self._payload["iat"] = datetime.utcnow().timestamp()

    def _set_type(self) -> None:
        self._payload["type"] = self._type


class AccessJWTTokenFactory(JWTTokenFactory):
    _type = TokenTypes.ACCESS.value


class RefreshJWTTokenFactory(JWTTokenFactory):
    _type = TokenTypes.REFRESH.value


class JWTRepository:
    def __init__(self,
                 secret_key: str
                 ):
        self.access = AccessJWTTokenFactory(
            secret_key=secret_key,
            lifetime_minutes=99999999)
