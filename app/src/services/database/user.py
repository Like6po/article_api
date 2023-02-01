from core.jwt import JWTRepository, TokenDataDTO
from core.password import verify_password, get_password_hash
from dto.token import TokenDTO, TokensDTO
from dto.user import LoginDTO
from models.user import UserModel
from services.database.base import DatabaseService


class UserNotExistsError(Exception):
    pass


class UserBadPasswordError(Exception):
    pass


class UserNotVerifiedError(Exception):
    pass


class UserExistsError(Exception):
    pass


class UserService(DatabaseService):
    model = UserModel

    @staticmethod
    def _create_user_tokens(jwt_repository: JWTRepository,
                            user_id: int) -> TokensDTO:
        access_token: TokenDataDTO = jwt_repository.access.create(user_id)

        return TokensDTO(
            access_token=TokenDTO(
                token=access_token.token,
                expire_at=access_token.expire_at
            )
        )

    async def login(self,
                    jwt_repository: JWTRepository,
                    email: str,
                    password: str) -> LoginDTO:
        user: UserModel | None = await self._get_one(UserModel.email == email)
        if not user:
            raise UserNotExistsError()
        if not user.is_verified:
            raise UserNotVerifiedError()
        if not verify_password(plain_password=password,
                               hashed_password=user.password_hash):
            raise UserBadPasswordError()

        user_tokens = self._create_user_tokens(jwt_repository=jwt_repository,
                                               user_id=user.id)

        return LoginDTO(sub=user.id,
                        access_token=TokenDTO(
                            token=user_tokens.access_token.token,
                            expire_at=user_tokens.access_token.expire_at
                        ))

    async def signup(self,
                     email: str,
                     password: str) -> None:
        user: UserModel | None = await self._get_one(UserModel.email == email)
        if user:
            return
        await self._add(email=email,
                        password_hash=get_password_hash(password))

    async def is_exists_by_email(self, email: str) -> bool:
        return await self._exists(UserModel.email == email)

    async def get_by_email(self, email: str) -> UserModel | None:
        return await self._get_one(UserModel.email == email)

    async def get_by_id(self, id: int) -> UserModel | None:
        return await self._get_one(UserModel.id == id)

    async def set_verified(self, email: str) -> None:
        return await self._update(UserModel.email == email, is_verified=True)
