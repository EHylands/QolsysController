import json
import logging
import uuid
from typing import TYPE_CHECKING, Any

from .errors import QolsysMqttError

if TYPE_CHECKING:
    import aiomqtt

    from .controller import QolsysController

LOGGER = logging.getLogger(__name__)


class MQTTCommand:
    def __init__(
        self,
        controller: "QolsysController",
        eventName: str,
    ) -> None:
        self._controller: QolsysController = controller
        self._client: aiomqtt.Client | None = controller.aiomqtt
        self._topic: str = "mastermeid"
        self._eventName: str = eventName
        self._payload: dict[str, Any] = {}
        self._requestID = str(uuid.uuid4())
        self._qos: int = self._controller.settings.mqtt_qos
        self._responseTopic = "response_" + self._controller.settings.random_mac

        self.append("requestID", self._requestID)
        self.append("responseTopic", self._responseTopic)
        self.append("eventName", self._eventName)
        self.append("remoteMacAddress", self._controller.settings.random_mac)

    def append(self, argument: str, value: str | dict[str, Any] | int | bool | list[dict[str, Any]] | Any) -> None:
        self._payload[argument] = value

    async def send_command(self) -> dict[str, Any]:
        if self._client is None:
            LOGGER.error("MQTT Client not configured")
            raise QolsysMqttError

        await self._client.publish(topic=self._topic, payload=json.dumps(self._payload), qos=self._qos)
        return await self._controller.mqtt_command_queue.wait_for_response(self._requestID)


class MQTTCommand_IpcCall(MQTTCommand):
    def __init__(
        self,
        controller: "QolsysController",
        ipc_service_name: str,
        ipc_interface_name: str,
        ipc_transaction_id: int,
    ) -> None:
        super().__init__(controller, "ipcCall")
        self.append("ipcServiceName", ipc_service_name)
        self.append("ipcInterfaceName", ipc_interface_name)
        self.append("ipcTransactionID", ipc_transaction_id)

    def append_ipc_request(self, ipc_request: list[dict[str, Any]]) -> None:
        self.append("ipcRequest", ipc_request)


class MQTTCommand_Panel(MQTTCommand_IpcCall):
    def __init__(
        self,
        controller: "QolsysController",
    ) -> None:
        super().__init__(
            controller=controller,
            ipc_service_name="qinternalservice",
            ipc_interface_name="android.os.IQInternalService",
            ipc_transaction_id=7,
        )


class MQTTCommand_ZWave(MQTTCommand_IpcCall):
    def __init__(
        self,
        controller: "QolsysController",
        node_id: str,
        zwave_command: list[int],
    ) -> None:
        super().__init__(
            controller=controller,
            ipc_service_name="qzwaveservice",
            ipc_interface_name="android.os.IQZwaveService",
            ipc_transaction_id=47,
        )

        ipc_request: list[dict[str, Any]] = [
            {
                "dataType": "int",
                "dataValue": int(node_id),
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "byteArray",
                "dataValue": zwave_command,
            },
            {
                "dataType": "int",
                "dataValue": 0,
            },
            {
                "dataType": "int",
                "dataValue": 106,
            },
            {
                "dataType": "byteArray",
                "dataValue": [0],
            },
        ]

        self.append_ipc_request(ipc_request)
