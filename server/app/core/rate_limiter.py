from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
    if settings.RATE_LIMIT_ENABLED and settings.RATE_LIMIT_PER_MINUTE
    else [],
    enabled=settings.RATE_LIMIT_ENABLED,
)
