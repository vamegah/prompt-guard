from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# The key_func determines how to identify a client.
# get_remote_address uses the client's IP address.
storage_uri = None
if settings.RATE_LIMIT_ENABLED and settings.RATE_LIMIT_STORAGE_URL:
    storage_uri = settings.RATE_LIMIT_STORAGE_URL

limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri)

# For a production environment with multiple server instances,
# you would want to use a shared backend like Redis. Since Redis is already
# in your stack, you could configure it like this:
# limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
