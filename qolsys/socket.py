import logging

LOGGER = logging.getLogger(__name__)

class QolsysSocket():
    def __init__(self,
                hostname: str,
                port: int,
                logger = None,
                connected_callback: callable = None,
                disconnected_callback: callable = None ) -> None:
    
        self._hostname = hostname
        self._port = port or 55555

        self._logger = logger or LOGGER

        self._writer = None

    def create_tasks(self, event_loop):
        return {
            'listen': event_loop.create_task(self.listen()),
        }

