import logging

LOGGER = logging.getLogger(__name__)

class QolsysSettings:

    def __init__(self) -> None:
        self._plugin_ip = ""
        self._plugin_paired = False
        self._random_mac = ""
        self._panel_mac = ""
        self._panel_ip = ""

    @property
    def plugin_paired(self) -> bool:
        return self._plugin_paired

    @plugin_paired.setter
    def plugin_paired(self, plugin_paired:bool) -> None:
        self._plugin_paired = plugin_paired

    @property
    def random_mac(self) -> str:
        return self._random_mac

    @random_mac.setter
    def random_mac(self,random_mac:str) -> None:
        self._random_mac = random_mac

    @property
    def plugin_ip(self) -> str:
        return self._plugin_ip

    @property
    def panel_mac(self) -> str:
        return self._panel_mac

    @panel_mac.setter
    def panel_mac(self,panel_mac:str) -> None:
        self._panel_mac = panel_mac

    @property
    def panel_ip(self) -> str:
        return self._panel_ip

    @panel_ip.setter
    def panel_ip(self, panel_ip:str) -> None:
        self._panel_ip = panel_ip

    def check_panel_ip(self) -> bool:
        if self._panel_ip == "":
            LOGGER.debug("Invalid Panel IP")
            return False

        LOGGER.debug("Found Panel IP")
        return True
