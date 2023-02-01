import datetime

from sqlalchemy import Column, TIMESTAMP, VARCHAR, func, INT, ForeignKey
from sqlalchemy.orm import relationship

from models.base import DatabaseModel


class CategoryModel(DatabaseModel):
    __tablename__ = 'categories'

    id = Column(INT,
                autoincrement=True,
                primary_key=True)
    created_at = Column(TIMESTAMP,
                        server_default=func.now(),
                        nullable=False)
    edited_at = Column(TIMESTAMP,
                       server_default=func.now(),
                       onupdate=datetime.datetime.utcnow,
                       nullable=False)
    name = Column(VARCHAR(32))
    user_id = Column(INT,
                     ForeignKey("users.id",
                                ondelete='CASCADE'),
                     nullable=True)

    user = relationship("UserModel",
                        back_populates="categories")

    articles = relationship(
        "ArticleModel",
        secondary="category_to_articles",
        back_populates="categories",
    )
