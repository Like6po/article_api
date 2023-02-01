from sqlalchemy import Column, TIMESTAMP, VARCHAR, INT, func, BOOLEAN
from sqlalchemy.orm import relationship

from models.base import DatabaseModel


class UserModel(DatabaseModel):
    __tablename__ = 'users'

    id = Column(INT,
                autoincrement=True,
                primary_key=True)
    created_at = Column(TIMESTAMP,
                        server_default=func.now())
    email = Column(VARCHAR(256),
                   unique=True,
                   index=True)
    password_hash = Column(VARCHAR(256))

    is_verified = Column(BOOLEAN,
                         server_default='0')

    categories = relationship(
        "CategoryModel",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    articles = relationship(
        "ArticleModel",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
