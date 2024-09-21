from __future__ import annotations
from typing import *

import time

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.integrations.redis import Redis


# предотсращение флуда от пользователей, 
# ограничение количества запросов за определенный период времени
# Redis хранит данные о лимитах для каждого пользователя

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, limit=2, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_manager = ThrottleManager(redis=redis)

        super(ThrottlingMiddleware, self).__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        try:
            await self.on_process_event(event)
        except CancelHandler:
            # Cancel current handler
            return

        try:
            result = await handler(event, data)
        except Exception as e:
            print(e)
            return

        return result

    async def on_process_event(self, event: Message) -> Any:
        limit = self.rate_limit
        key = f"{self.prefix}_message"

        # Use ThrottleManager.throttle method.
        try:
            await self.throttle_manager.throttle(key, rate=limit, user_id=event.from_user.id, chat_id=event.chat.id)
        except Throttled as t:
            # Execute action
            await self.event_throttled(event, t)
            # Cancel current handler
            raise CancelHandler()

    async def event_throttled(self, event: Message, throttled: Throttled):
        # Calculate how many time is left till the block ends
        delta = throttled.rate - throttled.delta
        # Prevent flooding
        if throttled.exceeded_count <= 2:
            await event.answer(f'Слишком много запросов.\nПопробуйте снова через {round(delta, 2)} секунд.')

# 
class ThrottleManager:
    bucket_keys = [
        "RATE_LIMIT", "DELTA",
        "LAST_CALL", "EXCEEDED_COUNT"
    ]

    def __init__(self, redis: Redis):
        self.redis = redis

    async def throttle(self, key: str, rate: float, user_id: int, chat_id: int):
        now = time.time()
        bucket_name = f'throttle_{key}_{user_id}_{chat_id}'

        data = await self.redis.hmget(bucket_name, self.bucket_keys)
        data = {
            k: float(v.decode()) 
               if isinstance(v, bytes) 
               else v 
            for k, v in zip(self.bucket_keys, data) 
            if v is not None
        }
        # Calculate
        called = data.get("LAST_CALL", now)
        delta = now - float(called)
        result = delta >= rate or delta <= 0
        # Save result
        data["RATE_LIMIT"] = rate
        data["LAST_CALL"] = now
        data["DELTA"] = delta
        if not result:
            data["EXCEEDED_COUNT"] = int(data["EXCEEDED_COUNT"])
            data["EXCEEDED_COUNT"] += 1
        else:
            data["EXCEEDED_COUNT"] = 1

        await self.redis.hmset(bucket_name, data)

        if not result:
            raise Throttled(key=key, chat=chat_id, user=user_id, **data)
        return result

# Исключение, генерируется если лимит запросов превышен
class Throttled(Exception):
    def __init__(self, **kwargs):
        self.key = kwargs.pop("key", '<None>')
        self.called_at = kwargs.pop("LAST_CALL", time.time())
        self.rate = kwargs.pop("RATE_LIMIT", None)
        self.exceeded_count = kwargs.pop("EXCEEDED_COUNT", 0)
        self.delta = kwargs.pop("DELTA", 0)
        self.user = kwargs.pop('user', None)
        self.chat = kwargs.pop('chat', None)

    def __str__(self):
        return f"Rate limit exceeded! (Limit: {self.rate} s, " \
               f"exceeded: {self.exceeded_count}, " \
               f"time delta: {round(self.delta, 3)} s)"


class CancelHandler(Exception):
    pass