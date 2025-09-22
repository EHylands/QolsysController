import asyncio


class QolsysMqttCommandQueue:
    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.waiters: dict[str, asyncio.Future] = {}

    async def handle_response(self, response:dict) -> None:
        requestID = response.get("requestID")

        if not requestID:
            msg = "MQTT Command response must have a requestID"
            raise ValueError(msg)

        async with self.lock:
            future = self.waiters.pop(requestID, None)

        if future and not future.done():
            future.set_result(response)

    async def wait_for_response(self,request_id:str) -> None:
        if request_id in self.waiters:
            msg = f"Duplicate waiter for request_id: {request_id}"
            raise ValueError(msg)

        future = asyncio.get_event_loop().create_future()
        async with self.lock:
            self.waiters[request_id] = future

        return await future

