import json
import hashlib
from typing import Any

from redis.asyncio import Redis


def build_cache_key(namespace: str, provider: str, model: str, prompt: str) -> str:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return f"{namespace}:{provider}:{model}:{digest}"


async def get_cached_text(redis: Redis, key: str) -> str | None:
    value = await redis.get(key)
    if not value:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    payload = json.loads(value)
    return payload.get("text")


async def set_cached_text(redis: Redis, key: str, text: str, ttl_seconds: int) -> None:
    payload = json.dumps({"text": text})
    await redis.set(key, payload, ex=ttl_seconds)
