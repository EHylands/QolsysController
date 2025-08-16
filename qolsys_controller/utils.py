import logging
import re
import subprocess

LOGGER = logging.getLogger(__name__)

class LoggerCallback(object):
    def __init__(self, msg=None):
        self.msg = msg or 'Logger callback'

    async def __call__(self, *args, **kwargs):
        LOGGER.debug(f"{self.msg}{': ' if args or kwargs else ''}"
                     f"{f'args={args} ' if args else ''}"
                     f"{f'kwargs={kwargs}' if kwargs else ''}")


async def defaultLoggerCallback(*args, **kwargs):
    callback = LoggerCallback()
    callback(*args, **kwargs)