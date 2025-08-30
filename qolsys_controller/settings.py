import logging

LOGGER = logging.getLogger(__name__)

class QolsysSettings:

    def __init__(self) -> None:
        self._plugin_ip = ""
        self._random_mac = ""
        self._panel_mac = ""
        self._panel_ip = ""

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

    @plugin_ip.setter
    def plugin_ip(self,plugin_ip:str) -> None:
        self._plugin_ip = plugin_ip

    def check_panel_ip(self) -> bool:
        if self._panel_ip == "":
            LOGGER.debug("Invalid Panel IP:  %s",self._panel_ip)
            return False

        LOGGER.debug("Found Panel IP: %s",self._panel_ip)
        return True

    def check_plugin_ip(self) -> bool:
        if self._plugin_ip == "":
            LOGGER.debug("Invalid Plugin IP:  %s",self._plugin_ip)
            return False

        LOGGER.debug("Found Plugin IP: %s",self._plugin_ip)
        return True
