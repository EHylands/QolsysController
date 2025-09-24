import logging

from .plugin import QolsysPlugin

LOGGER = logging.getLogger(__name__)

class QolsysPluginC4(QolsysPlugin):
        def __init__(self) -> None:

                # C4 Integration
                self._token = ""

        def config(self,panel_ip:str,token:str) -> bool:
                LOGGER.warning("C4Plugin: Configuring Plugin")
                super().config()
                return True


