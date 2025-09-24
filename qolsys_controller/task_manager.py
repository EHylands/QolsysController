import asyncio
import logging
from collections.abc import Coroutine

LOGGER = logging.getLogger(__name__)

class QolsysTaskManager:
    def __init__(self) -> None:
        self._tasks = set()

    def run(self, coro: Coroutine, label: str) -> asyncio.Task:
        task = asyncio.create_task(coro, name=label)
        self._tasks.add(task)

        def _done_callback(task: asyncio.Task) -> None:
            self._tasks.discard(task)

        task.add_done_callback(_done_callback)
        return task

    def cancel(self,label:str) -> None:
        for task in self._tasks:
            if task.get_name() == label:
                task.cancel()

    def cancel_all(self) -> None:
        for task in self._tasks:
            task.cancel()

    async def wait_all(self) -> None:
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    def pending(self) -> None:
        return {t for t in self._tasks if not t.done()}

    def dump(self) -> None:
        for task in self._tasks:
            LOGGER.debug("Task: %s, Done: %s, Cancelled: %s",task.get_name(),task.done(),task.cancelled())

