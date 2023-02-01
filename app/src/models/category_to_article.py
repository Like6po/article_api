from sqlalchemy import Column, INT, ForeignKey

from models.base import DatabaseModel


class CategoryToArticle(DatabaseModel):
    __tablename__ = 'category_to_articles'

    category_id = Column(INT,
                         ForeignKey("categories.id",
                                    ondelete='CASCADE'),
                         primary_key=True)
    article_id = Column(INT,
                        ForeignKey("articles.id",
                                   ondelete='CASCADE'),
                        primary_key=True)
