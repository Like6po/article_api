import datetime

from sqlalchemy import Column, TIMESTAMP, VARCHAR, func, INT, ForeignKey, TEXT
from sqlalchemy.orm import relationship

from models.base import DatabaseModel


class ArticleModel(DatabaseModel):
    __tablename__ = 'articles'

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
    title = Column(VARCHAR(32),
                   nullable=False)
    text = Column(TEXT, nullable=False)
    user_id = Column(INT,
                     ForeignKey("users.id",
                                ondelete='CASCADE'),
                     nullable=True)

    user = relationship("UserModel",
                        back_populates="articles")

    categories = relationship(
        "CategoryModel",
        secondary="category_to_articles",
        back_populates="articles"
    )
