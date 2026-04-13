import asyncio
import logging
from typing import TYPE_CHECKING, Any

# from qolsys_controller.mqtt_bridge.auth_plugin import AuthPlugin

LOGGER = logging.getLogger(__name__)
logging.getLogger("transitions.core").setLevel(logging.ERROR)
logging.getLogger("amqtt").setLevel(logging.ERROR)
logging.getLogger("amqtt.core").setLevel(logging.ERROR)
logging.getLogger("amqtt.broker").setLevel(logging.ERROR)
logging.getLogger("amqtt.plugins").setLevel(logging.ERROR)


if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController
    from qolsys_controller.mqtt_bridge.bridge import MqttBridge


class MqttBridgeBroker:
    def __init__(self, bridge: "MqttBridge") -> None:
        self._bridge: MqttBridge = bridge
        self._controller: QolsysController = bridge._controller
        self._config: dict[str, Any] = {}
        self._broker: Any = None
        self._is_running: bool = False
        self._broker_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    def _import_amqtt(self) -> tuple[Any, Any, Any, Any]:
        from amqtt.broker import Broker
        from amqtt.contexts import BaseContext
        from amqtt.plugins.authentication import BaseAuthPlugin
        from amqtt.session import Session

        return Broker, BaseContext, BaseAuthPlugin, Session

    def load_auth_plugin(self, enabled: bool) -> Any | None:
        if not enabled:
            return None
        from .auth_plugin import AuthPlugin

        return AuthPlugin

    async def start(self) -> bool:
        if self._is_running:
            return True

        if self._broker_task and not self._broker_task.done():
            LOGGER.warning("MQTT Bridge Broker: Start requested while broker task is already running")
            return False

        LOGGER.info(
            "MQTT Bridge Broker: Starting: %s:%s ...",
            self._controller.settings.plugin_ip,
            self._controller.settings.mqtt_bridge_port,
        )

        startup_event = asyncio.Event()
        startup_result: dict[str, bool | Exception] = {"started": False}
        self._stop_event.clear()
        self._broker_task = asyncio.create_task(self._run(startup_event, startup_result))

        await startup_event.wait()

        result = startup_result.get("started")
        if result is True:
            return True

        broker_error = startup_result.get("error")
        if isinstance(broker_error, Exception):
            LOGGER.error("MQTT Bridge Broker: Error Starting: %s", broker_error)

        if self._broker_task.done():
            try:
                await self._broker_task
            except Exception:
                pass

        self._broker_task = None
        return False

    async def _run(self, startup_event: asyncio.Event, startup_result: dict[str, bool | Exception]) -> None:
        try:
            if self._controller.settings.mqtt_bridge_tls_enabled:
                await self._check_or_create_certificates()
            self._config = self._build_config()
            self._broker = self._create_broker()
            if self._broker is None:
                startup_result["started"] = False
                startup_event.set()
                return
            await self._broker.start()
            await self.wait_for_broker_start()
            self._broker.on_client_connected = self._on_client_connected
            self._broker.on_packet_received = self._on_packet_received

            self._is_running = True
            startup_result["started"] = True
            startup_event.set()

            # Wait forever until cancelled
            await self._stop_event.wait()

        except asyncio.CancelledError:
            pass

        except Exception as err:
            self._is_running = False
            startup_result["error"] = err
            startup_event.set()
            LOGGER.error("MQTT Bridge Broker: Runtime error: %s", err)
            raise

        finally:
            self._is_running = False

            if not startup_event.is_set():
                startup_result["started"] = False
                startup_event.set()

            try:
                await asyncio.wait_for(
                    asyncio.shield(self._broker.shutdown()),
                    timeout=5,
                )

            except asyncio.TimeoutError:
                LOGGER.warning("MQTT Bridge Broker: Shutdown timed out")

            except Exception as err:
                LOGGER.debug("MQTT Bridge Broker: Error during shutdown: %s", err)

    async def _on_client_connected(self, client_id: str) -> None:
        LOGGER.info("MQTT Bridge Broker: Client connected: %s", client_id)

    async def _on_packet_received(self, client_id: str, topic: str, payload: bytes) -> None:
        LOGGER.debug("MQTT Bridge Broker: Packet received from client %s on topic %s: %s", client_id, topic, payload)

    async def wait_for_broker_start(self, timeout: int = 5) -> None:
        start_time = asyncio.get_event_loop().time()
        while self._broker.transitions.state != "started":
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("MQTT Bridge Broker did not start in time")
            await asyncio.sleep(0.05)
        LOGGER.info("MQTT Bridge Broker: Running")

    async def _check_or_create_certificates(self) -> None:
        if (
            not await self._controller._pki.check_mqtt_bridge_key_file()
            or not await self._controller._pki.check_mqtt_bridge_cer_file()
        ):
            LOGGER.debug("MQTT Bridge Broker: Certificates not found, creating new certificates")
            await self._controller._pki.create_mqtt_bridge_certificates()

    def _create_broker(self) -> Any:
        if not self._controller.settings.mqtt_bridge_enabled:
            return None

        Broker, _, _, _ = self._import_amqtt()
        broker = Broker(self._config)
        return broker

    def _build_config(self) -> dict[str, Any]:
        if not self._controller.settings.mqtt_bridge_enabled:
            return {}

        listener: dict[str, Any] = {
            "type": "tcp",
            "bind": f"{self._controller.settings.plugin_ip}:{self._controller.settings.mqtt_bridge_port}",
            "ssl": self._controller.settings.mqtt_bridge_tls_enabled,
            "max_connections": self._controller.settings.mqtt_bridge_max_connections,
        }

        if self._controller.settings.mqtt_bridge_tls_enabled:
            listener["certfile"] = str(self._controller._pki.mqtt_bridge_cer_file_path)
            listener["keyfile"] = str(self._controller._pki.mqtt_bridge_key_file_path)

        listeners = {"default": listener}

        # Plugin selection
        plugins: dict[str, dict[str, Any]] = {}
        if self._controller.settings.mqtt_bridge_enabled:
            plugins["qolsys_controller.mqtt_bridge.auth_plugin.AuthPlugin"] = {
                "allowed_users": self._controller.settings.mqtt_bridge_allowed_users
            }

        return {"listeners": listeners, "plugins": plugins}

    async def shutdown(self) -> None:
        LOGGER.info("MQTT Bridge Broker: Shutting down ...")
        if self._broker_task:
            self._stop_event.set()
            await self._broker_task
            self._broker_task = None
            LOGGER.info("MQTT Bridge Broker: Shutdown complete")
