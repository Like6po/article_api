from core.settings import SETTINGS
from services.redis import RedisService

redis_service = RedisService(connect_url=SETTINGS.REDIS.build_url())


def get_redis_service() -> RedisService:
    return redis_service
