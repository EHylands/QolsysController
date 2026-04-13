import logging
import secrets
import string
from typing import TYPE_CHECKING

from passlib.hash import sha512_crypt

from .broker import MqttBridgeBroker
from .client import MqttBridgeClient

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class MqttBridge:
    def __init__(self, controller: "QolsysController") -> None:
        self._controller = controller
        self._broker: MqttBridgeBroker | None = None
        self._client: MqttBridgeClient | None = None
        self._is_running = False

        self._version = "1"
        self._mqtt_timeout = 15
        self._mqtt_qos = 1

        self._settings_topic = "settings"
        self._status_topic = "status"
        self._zone_topic = "zone"
        self._partition_topic = "partition"
        self._automation_topic = "automation"
        self._panel_topic = "panel"
        self._scene_topic = "scene"

        self._internal_user = "internal_user"
        self._internal_password = ""

        # Create randon internal_user password
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        self._internal_password = "".join(secrets.choice(alphabet) for _ in range(16))

        # Check if internal_user in allowed_users database
        if self._internal_user in self._controller.settings.mqtt_bridge_allowed_users:
            LOGGER.error(
                "MQTT Bridge: Internal user '%s' already exists in allowed_users. This is a security risk. Please remove the internal user from allowed_users and restart the MQTT Bridge.",
                self._internal_user,
            )
        self._controller.settings.mqtt_bridge_allowed_users[self._internal_user] = sha512_crypt.hash(self._internal_password)

    async def start(self) -> bool:
        if self._is_running:
            LOGGER.warning("MQTT Bridge: Allready running")
            return True

        LOGGER.info("MQTT Bridge Starting ...")

        # Create MQTT Bridge Broker if not already created
        if not self._broker:
            self._broker = MqttBridgeBroker(self)

        # Start MQTT Bridge Broker
        if not await self._broker.start():
            LOGGER.error("MQTT Bridge Broker failed to start. MQTT Bridge will not start.")
            return False

        # Create MQTT Bridge Client if not already created
        if not self._client:
            self._client = MqttBridgeClient(self)

        # Start MQTT Bridge Client
        if not await self._client.start():
            LOGGER.error("MQTT Bridge Client failed to connect. MQTT Bridge will not start.")
            return False

        LOGGER.info("MQTT Bridge Running")
        self._is_running = True
        return True

    async def shutdown(self) -> None:
        LOGGER.debug("MQTT Bridge: Shutting down ...")
        self._is_running = False
        try:
            if self._client:
                await self._client.shutdown()
        finally:
            if self._broker:
                await self._broker.shutdown()

        LOGGER.debug("MQTT Bridge: Shutdown complete")

    @property
    def panel_unique_id(self) -> str:
        if self._controller.settings.mqtt_bridge_friendly_name != "":
            return self._controller.settings.mqtt_bridge_friendly_name
        return self._controller.panel.unique_id

    @property
    def version(self) -> str:
        return self._version

    @property
    def base_topic(self) -> str:
        return f"{self._controller.settings.mqtt_bridge_root_topic}/v{self.version}/{self.panel_unique_id}"

    @property
    def automation_topic(self) -> str:
        return f"{self.base_topic}/{self._automation_topic}"

    @property
    def partition_topic(self) -> str:
        return f"{self.base_topic}/{self._partition_topic}"

    @property
    def zone_topic(self) -> str:
        return f"{self.base_topic}/{self._zone_topic}"

    @property
    def settings_topic(self) -> str:
        return f"{self.base_topic}/panel/{self._settings_topic}"

    @property
    def status_topic(self) -> str:
        return f"{self.base_topic}/panel/{self._status_topic}"

    @property
    def scene_topic(self) -> str:
        return f"{self.base_topic}/{self._scene_topic}"

    @property
    def automation_command_topic(self) -> str:
        return f"{self.automation_topic}/+/command"

    @property
    def partition_command_topic(self) -> str:
        return f"{self.partition_topic}/+/command"

    @property
    def panel_command_topic(self) -> str:
        return f"{self.base_topic}/panel/command"

    @property
    def command_topics(self) -> list[str]:
        return [
            self.automation_command_topic,
            self.partition_command_topic,
            self.panel_command_topic,
        ]

    @property
    def mqtt_timeout(self) -> int:
        return self._mqtt_timeout

    @property
    def mqtt_qos(self) -> int:
        return self._mqtt_qos
