import asyncio
import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


class QolsysMqttCommandQueue:
    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.waiters: dict[str, asyncio.Future[Any]] = {}

    async def handle_response(self, response: dict[str, str]) -> None:
        LOGGER.debug("MQTT Command response received: %s", response)
        requestID = response.get("requestID")

        if not requestID:
            LOGGER.error("MQTT Command response missing requestID: %s", response)
            return

        async with self.lock:
            future = self.waiters.pop(requestID, None)

        if future and not future.done():
            future.set_result(response)

    async def wait_for_response(self, request_id: str, timeout: int = 30) -> dict[str, Any]:  # type: ignore[return]
        LOGGER.debug("Waiting for MQTT Command response with request_id: %s", request_id)
        future = asyncio.get_running_loop().create_future()
        async with self.lock:
            if request_id == "":
                raise ValueError("request_id cannot be empty")

            if request_id in self.waiters:
                msg = f"Duplicate waiter for request_id: {request_id}"
                raise ValueError(msg)

            self.waiters[request_id] = future

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            LOGGER.debug(f"MQTT Command timed out for request_id: {request_id}")
        finally:
            # Ensure cleanup even if timeout or cancellation happens
            async with self.lock:
                self.waiters.pop(request_id, None)
