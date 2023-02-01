from models import UserModel, CategoryModel, ArticleModel


async def load_fixtures(session_factory):
    s = session_factory()
    try:
        test_user = UserModel(email="user@example.com",
                              password_hash="$2b$12$Doas1u0btJOsvB4J06ZCXe1giuFaiqukmGWWjgTsUnPjuxgFVilK2",
                              is_verified=True)
        s.add(test_user)
        await s.flush()
        test_category = CategoryModel(name="Тестовая категория",
                                      user_id=test_user.id)
        s.add(test_category)
        await s.flush()
        test_article = ArticleModel(title="Тестовая статья",
                                    text="Текст тестовой статьи",
                                    user_id=test_user.id)
        test_article.categories.append(test_category)
        s.add(test_article)
        await s.commit()
    finally:
        await s.close()
