from redis.asyncio import Redis, from_url

from backend.app.core.config import settings

redis_client: Redis = from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


async def close_redis() -> None:
    await redis_client.aclose()