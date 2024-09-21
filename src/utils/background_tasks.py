from typing import Any

from asyncio import Task


tg_background_tasks: set[Task[Any]] = set()
