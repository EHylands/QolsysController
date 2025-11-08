from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .controller import QolsysController


class QolsysSettings:

    def __init__(self, controller: QolsysController) -> None:

        # Main controller
        self._controller = controller

        # Plugin
        self._plugin_ip: str = ""
        self._random_mac: str = ""
        self._panel_mac: str  = ""
        self._panel_ip: str = ""

        # Path
        self._config_directory: Path = Path()
        self._pki_directory: Path = Path()
        self._media_directory: Path = Path()
        self._users_file_path: Path = Path()

        # Pki
        self._key_size: int = 2048

        # MQTT
        self._mqtt_timeout: int = 30
        self._mqtt_ping: int = 600
        self._mqtt_qos: int = 0
        self._mqtt_remote_client_id: str = ""

        # Operation
        self._motion_sensor_delay: bool = True
        self._motion_sensor_delay_sec: int = 310

    @property
    def random_mac(self) -> str:
        return self._random_mac

    @random_mac.setter
    def random_mac(self, random_mac: str) -> None:
        self._random_mac = random_mac.lower()

    @property
    def plugin_ip(self) -> str:
        return self._plugin_ip

    @property
    def panel_mac(self) -> str:
        return self._panel_mac

    @panel_mac.setter
    def panel_mac(self, panel_mac: str) -> None:
        self._panel_mac = panel_mac

    @property
    def panel_ip(self) -> str:
        return self._panel_ip

    @property
    def mqtt_timeout(self) -> int:
        return self._mqtt_timeout

    @property
    def mqtt_ping(self) -> int:
        return self._mqtt_ping

    @property
    def motion_sensor_delay(self) -> bool:
        return self._motion_sensor_delay

    @property
    def motion_sensor_delay_sec(self) -> int:
        return self._motion_sensor_delay_sec

    @motion_sensor_delay.setter
    def motion_sensor_delay(self, value: bool) -> None:
        self._motion_sensor_delay = value

    @motion_sensor_delay_sec.setter
    def motion_sensor_delay_sec(self, value: int) -> None:
        self._motion_sensor_delay_sec = value

    @panel_ip.setter
    def panel_ip(self, panel_ip: str) -> None:
        self._panel_ip = panel_ip

    @plugin_ip.setter
    def plugin_ip(self, plugin_ip: str) -> None:
        self._plugin_ip = plugin_ip

    @property
    def config_directory(self) -> Path:
        return self._config_directory

    @config_directory.setter
    def config_directory(self, config_directory: str) -> None:
        self._config_directory = Path(config_directory)
        self._pki_directory = self._config_directory.joinpath("pki")
        self._media_directory = self._config_directory.joinpath("media")
        self._users_file_path = self._config_directory.joinpath("users.conf")

    @property
    def pki_directory(self) -> Path:
        return self._pki_directory

    @property
    def users_file_path(self) -> Path:
        return self._users_file_path

    @property
    def key_size(self) -> int:
        return self._key_size

    @mqtt_timeout.setter
    def mqtt_timeout(self, value: int) -> None:
        self._mqtt_timeout = value

    @mqtt_ping.setter
    def mqtt_ping(self, value: int) -> None:
        self._mqtt_ping = value

    @property
    def mqtt_qos(self) -> int:
        return self._mqtt_qos

    @property
    def mqtt_remote_client_id(self) -> str:
        return self._mqtt_remote_client_id

    @mqtt_remote_client_id.setter
    def mqtt_remote_client_id(self,client_id: str) -> None:
        self._mqtt_remote_client_id = client_id

    def check_panel_ip(self) -> bool:
        if self._panel_ip == "":
            LOGGER.debug("Invalid Panel IP:  %s", self._panel_ip)
            return False

        LOGGER.debug("Found Panel IP: %s", self._panel_ip)
        return True

    def check_plugin_ip(self) -> bool:
        if self._plugin_ip == "":
            LOGGER.debug("Invalid Plugin IP:  %s", self._plugin_ip)
            return False

        LOGGER.debug("Found Plugin IP: %s", self._plugin_ip)
        return True

    def check_config_directory(self, create: bool = True) -> bool:  # noqa: PLR0911
        if not self.config_directory.is_dir():
            if not create:
                LOGGER.debug("config_directory not found:  %s", self.config_directory)
                return False

            # Create config directory if not found
            LOGGER.debug("Creating config_directory: %s", self.config_directory)
            try:
                self.config_directory.mkdir(parents=True)
            except PermissionError:
                LOGGER.exception("Permission denied: Unable to create: %s", self.config_directory)
                return False
            except Exception:
                LOGGER.exception("Error creating config_directory: %s", self.config_directory)
                return False

        LOGGER.debug("Using config_directory: %s", self.config_directory.resolve())

        # Create pki directory if not found
        if not self.pki_directory.is_dir():
            LOGGER.debug("Creating pki_directory: %s", self.pki_directory.resolve())
            try:
                self.pki_directory.mkdir(parents=True)
            except PermissionError:
                LOGGER.exception("Permission denied: Unable to create: %s", self.pki_directory.resolve())
                return False
            except Exception:
                LOGGER.exception("Error creating pki_directory: %s", self.pki_directory.resolve())
                return False

        LOGGER.debug("Using pki_directory: %s", self.pki_directory.resolve())

        # Create media directory if not found
        if not self._media_directory.is_dir():
            LOGGER.debug("Creating media_directory: %s", self._media_directory.resolve())
            try:
                self._media_directory.mkdir(parents=True)
            except PermissionError:
                LOGGER.exception("Permission denied: Unable to create: %s", self._media_directory.resolve())
                return False
            except Exception:
                LOGGER.exception("Error creating media_directory: %s", self._media_directory.resolve())
                return False

        LOGGER.debug("Using media_directory: %s", self._media_directory.resolve())

        return True
